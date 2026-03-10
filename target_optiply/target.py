"""Optiply target class."""
from target_optiply.sinks import (
    BaseOptiplySink,
    ProductsSink,
    SupplierSink,
    SupplierProductSink,
    BuyOrderSink,
    BuyOrderLineSink,
    SellOrderSink,
    SellOrderLineSink,
)

from target_hotglue.target import TargetHotglue
from typing import Callable, Dict, List, Optional, Tuple, Type, Union
from pathlib import Path, PurePath


class TargetOptiply(TargetHotglue):
    """Target for Optiply."""

    def __init__(
        self,
        config: Optional[Union[dict, PurePath, str, List[Union[PurePath, str]]]] = None,
        parse_env_config: bool = False,
        validate_config: bool = True,
        state: str = None
    ) -> None:
        self.config_file = config[0]
        self.logger.info(f"Target config file: {self.config_file}")
        super().__init__(config, parse_env_config, validate_config)
        
        # Log the config structure after initialization
        self.logger.info(f"Target config keys: {list(self._config.keys())}")
        
        # Log the access_token being used
        if "access_token" in self._config:
            access_token = self._config["access_token"]
            # Log first few characters of token for security
            if access_token and len(access_token) > 8:
                masked_token = access_token[:4] + "*" * (len(access_token) - 8) + access_token[-4:]
                self.logger.info(f"Using access_token: {masked_token}")
            else:
                self.logger.info(f"Using access_token: {access_token}")
        else:
            self.logger.warning("No access_token found in config")
        
        # Also check for "token" key for backward compatibility
        if "token" in self._config:
            token = self._config["token"]
            # Log first few characters of token for security
            if token and len(token) > 8:
                masked_token = token[:4] + "*" * (len(token) - 8) + token[-4:]
                self.logger.info(f"Using token: {masked_token}")
            else:
                self.logger.info(f"Using token: {token}")
        else:
            self.logger.info("No token key found in config (using access_token instead)")

    SINK_TYPES = [
        BaseOptiplySink,
        ProductsSink,
        SupplierSink,
        SupplierProductSink,
        BuyOrderSink,
        BuyOrderLineSink,
        SellOrderSink,
        SellOrderLineSink,
    ]
    MAX_PARALLELISM = 10
    name = "target-optiply"
    EXTERNAL_ID_KEY = "remoteId" # This is the key that will be used to resolve the external ID
    GLOBAL_PRIMARY_KEY = "optiply_id"

    def get_sink_class(self, stream_name: str):
        """Get sink class for the given stream name."""
        # Map stream names to sink classes
        sink_map = {
            "BuyOrders": BuyOrderSink,
            "Products": ProductsSink,
            "Suppliers": SupplierSink,
            "SupplierProducts": SupplierProductSink,
            "BuyOrderLines": BuyOrderLineSink,
            "SellOrders": SellOrderSink,
            "SellOrderLines": SellOrderLineSink,
        }
        
        return sink_map.get(stream_name, BaseOptiplySink)

    def _simplify_records_dict(self, records_dict: dict) -> dict:
        """Helper method to simplify records dictionary to show only counts."""
        simplified_dict = {}
        for stream_name, records in records_dict.items():
            if isinstance(records, list):
                # Count successes and failures
                success_count = sum(1 for record in records if record.get("success", False))
                fail_count = len(records) - success_count
                
                simplified_dict[stream_name] = {
                    "total": len(records),
                    "success": success_count,
                    "failed": fail_count
                }
            else:
                # Keep as is if not a list
                simplified_dict[stream_name] = records
        
        return simplified_dict

    def get_state(self) -> dict:
        """Override to provide simplified state with only counts."""
        # Get the original state from parent
        original_state = super().get_state()
        
        # Simplify the bookmarks to only show counts
        if "bookmarks" in original_state:
            original_state["bookmarks"] = self._simplify_records_dict(original_state["bookmarks"])
        
        return original_state

    def _get_export_summary(self) -> dict:
        """Override to provide simplified export summary."""
        # Get the original export summary from parent
        original_summary = super()._get_export_summary()
        
        # Simplify the export details to only show counts
        if "exportDetails" in original_summary:
            original_summary["exportDetails"] = self._simplify_records_dict(original_summary["exportDetails"])
        
        return original_summary

    def _get_export_details(self) -> dict:
        """Override to provide simplified export details."""
        # Get the original export details from parent
        original_details = super()._get_export_details()
        
        # Simplify the export details to only show counts
        return self._simplify_records_dict(original_details)

    def _get_metrics(self) -> dict:
        """Override to provide simplified metrics."""
        # Get the original metrics from parent
        original_metrics = super()._get_metrics()
        
        # Simplify the export details to only show counts
        if "exportDetails" in original_metrics:
            original_metrics["exportDetails"] = self._simplify_records_dict(original_metrics["exportDetails"])
        
        return original_metrics


if __name__ == "__main__":
    TargetOptiply.cli()
