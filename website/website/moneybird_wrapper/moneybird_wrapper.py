"""Moneybird API wrapper."""
from moneybird import MoneyBird
from moneybird import TokenAuthentication


class MoneyBirdWrapper:
    """A Moneybird API wrapper."""

    def __init__(self, key: str):
        """
        Initialize the Moneybird Wrapper.

        :key: the API key
        """
        self.api = MoneyBird(TokenAuthentication(key))
        self.administration_id = self.api.get("administrations")[0]["id"]

    def __load_documents(self, document_type: str):
        """
        Load the documents of the specified type.

        :param document_type: the type of document we want to load
        :return: requested documents as JSON
        """
        documents = self.api.get(
            f"documents/{document_type}/synchronization",
            administration_id=self.administration_id,
        )
        # We can request at most 100 documents in one go
        split = [documents[x : x + 100] for x in range(0, len(documents), 100)]

        return_data = []
        for split_documents in split:
            # Get all document ids
            ids = [document["id"] for document in split_documents]

            # Prepare the ids dictionary
            request_ids = {"ids": ids}
            requested_documents = self.api.post(
                f"documents/{document_type}/synchronization",
                data=request_ids,
                administration_id=self.administration_id,
            )
            return_data.extend(requested_documents)

        return return_data

    def load_purchase_invoices(self):
        """
        Load purchase invoices.

        :return: purchase invoices as JSON
        """
        return self.__load_documents("purchase_invoices")

    def load_receipts(self):
        """
        Load receipts.

        :return: receipts as JSON
        """
        return self.__load_documents("receipts")
