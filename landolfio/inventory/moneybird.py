from typing import Any, Dict

from moneybird.administration import get_moneybird_administration


class MoneybirdAssetService:
    def __init__(self):
        self.admin = get_moneybird_administration()

    def create_asset(
        self,
        name: str,
        ledger_account_id: int,
        purchase_value: float,
        start_date: str,
    ) -> Dict[str, Any]:
        """
        Create a new asset on Moneybird.

        Args:
            name: Asset name
            ledger_account_id: ID of the ledger account
            purchase_value: Purchase value
            start_date: Start date in YYYY-MM-DD format (used as purchase_date)

        Returns:
            Dict containing the created asset data
        """

        data = {
            "asset": {
                "name": name,
                "ledger_account_id": ledger_account_id,
                "purchase_date": start_date,
                "purchase_value": purchase_value,
                "value_change_plan_attributes": {
                    "lifespan_in_years": 30,
                    "residual_value": purchase_value,
                },
            }
        }

        return self.admin.post("assets", data)

    def get_asset_financial_info(self, asset_id: int) -> Dict[str, Any]:
        """
        Get current financial information of an asset from Moneybird.

        Args:
            asset_id: The asset ID

        Returns:
            Dict containing asset financial data including current value,
            depreciation info, and value change history
        """
        return self.admin.get(f"assets/{asset_id}")

    def delete_asset(self, asset_id: int) -> bool:
        """
        Delete an asset from Moneybird.

        Args:
            asset_id: The asset ID to delete

        Returns:
            True if deletion was successful

        Raises:
            Exception if deletion fails
        """
        try:
            self.admin.delete(f"assets/{asset_id}")
            return True
        except Exception as e:
            raise Exception(
                f"Failed to delete asset {asset_id} from Moneybird: {str(e)}"
            )

    def update_asset(
        self,
        asset_id: int,
        name: str = None,
        ledger_account_id: int = None,
        purchase_date: str = None,
        purchase_value: float = None,
    ) -> Dict[str, Any]:
        """
        Update an existing asset on Moneybird.

        Args:
            asset_id: The asset ID to update
            name: Asset name
            ledger_account_id: ID of the ledger account
            purchase_date: Purchase date in YYYY-MM-DD format
            purchase_value: Purchase value

        Returns:
            Dict containing the updated asset data
        """
        data = {"asset": {}}

        if name is not None:
            data["asset"]["name"] = name
        if ledger_account_id is not None:
            data["asset"]["ledger_account_id"] = ledger_account_id
        if purchase_date is not None:
            data["asset"]["purchase_date"] = purchase_date
        if purchase_value is not None:
            data["asset"]["purchase_value"] = purchase_value

        return self.admin.patch(f"assets/{asset_id}", data)

    def dispose_asset(
        self,
        asset_id: int,
        disposal_date: str,
        disposal_reason: str,
    ) -> Dict[str, Any]:
        """
        Dispose an asset on Moneybird.

        Args:
            asset_id: The asset ID to dispose
            disposal_date: Disposal date in YYYY-MM-DD format
            disposal_reason: Disposal reason (out_of_use, sold, private_withdrawal, divested)

        Returns:
            Dict containing the disposal response data
        """
        data = {"date": disposal_date, "reason": disposal_reason}

        return self.admin.post(f"assets/{asset_id}/disposals", data)

    def fully_depreciate_asset(
        self,
        asset_id: int,
        depreciation_date: str,
        description: str = "Full depreciation before disposal",
    ) -> Dict[str, Any]:
        """
        Fully depreciate an asset on Moneybird.

        Args:
            asset_id: The asset ID to depreciate
            depreciation_date: Depreciation date in YYYY-MM-DD format
            description: Description for the depreciation

        Returns:
            Dict containing the depreciation response data
        """
        data = {"date": depreciation_date, "description": description}

        return self.admin.post(
            f"assets/{asset_id}/value_changes/full_depreciation", data
        )

    def create_manual_value_change(
        self,
        asset_id: int,
        change_date: str,
        amount: float,
        description: str,
        externally_booked: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a manual value change for the asset.

        Args:
            asset_id: The asset ID
            change_date: Change date in YYYY-MM-DD format
            amount: Amount (negative decreases value, positive increases value)
            description: Description for the value change
            externally_booked: Whether the value change is already externally booked

        Returns:
            Dict containing the value change response data
        """
        data = {
            "date": change_date,
            "amount": amount,
            "description": description,
            "externally_booked": externally_booked,
        }

        return self.admin.post(f"assets/{asset_id}/value_changes/manual", data)

    def create_arbitrary_value_change(
        self,
        asset_id: int,
        change_date: str,
        amount: float,
        description: str,
        externally_booked: bool = False,
    ) -> Dict[str, Any]:
        """
        Create an arbitrary value change for the asset.

        Args:
            asset_id: The asset ID
            change_date: Change date in YYYY-MM-DD format
            amount: Amount (negative decreases value, positive increases value)
            description: Description for the value change
            externally_booked: Whether the value change is already externally booked

        Returns:
            Dict containing the value change response data
        """
        data = {
            "date": change_date,
            "amount": amount,
            "description": description,
            "externally_booked": externally_booked,
        }

        return self.admin.post(f"assets/{asset_id}/value_changes/arbitrary", data)

    def create_divestment_value_change(
        self,
        asset_id: int,
        change_date: str,
        description: str = "Verkocht",
    ) -> Dict[str, Any]:
        """
        Create a divestment value change for the asset.
        This will automatically set the amount to the asset's current value
        and create a disposal record.

        Args:
            asset_id: The asset ID
            change_date: Change date in YYYY-MM-DD format
            description: Description for the divestment

        Returns:
            Dict containing the value change response data
        """
        data = {"date": change_date, "description": description}

        return self.admin.post(f"assets/{asset_id}/value_changes/divestment", data)
