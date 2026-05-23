from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID
from decimal import Decimal
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/functions", tags=["Functions & Procedures"])


@router.get("/account-balance/{account_id}", response_model=schemas.AccountBalanceResponse)
def get_account_balance(
        account_id: UUID,
        db: Session = Depends(get_db)
):
    try:
        result = db.execute(
            text("SELECT * FROM get_account_balance(:account_id)"),
            {"account_id": account_id}
        ).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_id} not found"
            )

        return {
            "balance_calc": result[0],
            "currency": result[1],
            "last_transaction_date": result[2]
        }
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get account balance: {error_msg}"
        )


@router.post("/check-transfer", response_model=schemas.TransferEligibilityResponse)
def check_transfer_eligibility(
        request: schemas.TransferRequest,
        db: Session = Depends(get_db)
):
    try:
        result = db.execute(
            text("""
                SELECT * FROM check_transfer_eligibility(
                    :p_from_account_id, 
                    :p_to_account_id, 
                    :p_amount
                )
            """),
            {
                "p_from_account_id": request.from_account_id,
                "p_to_account_id": request.to_account_id,
                "p_amount": request.amount
            }
        ).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Function returned no result"
            )

        return {
            "is_possible": result[0],
            "fee": result[1] or 0,
            "message": result[2]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transfer check failed: {str(e)}"
        )


@router.post("/transfer", response_model=schemas.TransferResponse, status_code=status.HTTP_201_CREATED)
def transfer_money(
        request: schemas.TransferRequest,
        db: Session = Depends(get_db)
):
    try:
        db.execute(
            text("""
                CALL transfer_money(
                    :p_from_account_id, 
                    :p_to_account_id, 
                    :p_amount, 
                    :p_description
                )
            """),
            {
                "p_from_account_id": request.from_account_id,
                "p_to_account_id": request.to_account_id,
                "p_amount": request.amount,
                "p_description": request.description
            }
        )
        db.commit()

        return {
            "success": True,
            "message": "Transfer completed successfully",
            "from_account_id": request.from_account_id,
            "to_account_id": request.to_account_id,
            "amount": request.amount,
            "fee": 0
        }
    except Exception as e:
        db.rollback()
        error_msg = str(e)

        if "not enough money" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient funds: {error_msg}"
            )
        elif "similar accounts" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer to the same account"
            )
        elif "category" in error_msg.lower() and "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Required categories 'Transfer' or 'Commission' not found for this user"
            )
        elif "currency conversion" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transfer failed: {error_msg}"
            )