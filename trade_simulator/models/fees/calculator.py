from dataclasses import dataclass
from typing import Dict, Optional, Union
from trade_simulator.utils.logging import get_logger
from trade_simulator.utils.exceptions import ModelError

@dataclass
class FeeStructure:
    """Represents the fee structure for an exchange"""
    maker_fee: float
    taker_fee: float
    volume_thresholds: Dict[float, float]  # USD volume to fee discount

class FeeCalculator:
    """
    Calculates trading fees based on exchange fee schedules and trade parameters.
    Supports tiered fee structures and maker/taker differentiation.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.exchange_fees = {
            'OKX': self._load_okx_fee_schedule(),
            'BINANCE': self._load_binance_fee_schedule(),
        }
        
    def calculate(self,
                 notional_value: float,
                 exchange: Union[str, int] = 'OKX',
                 fee_tier: int = 1,
                 is_maker: bool = False) -> float:
        """
        Calculate fees for a trade.
        
        Args:
            notional_value: Trade value in quote currency (e.g., USD)
            exchange: Exchange name (must be in exchange_fees)
            fee_tier: User's fee tier (1 = base tier)
            is_maker: Whether the order provides liquidity
            
        Returns:
            Calculated fee amount in quote currency
        """
        try:
            if notional_value <= 0:
                return 0.0
                
            # Safely handle exchange parameter
            exchange_str = str(exchange).strip().upper()
            if not exchange_str:
                exchange_str = 'OKX'  # default
                
            fee_structure = self.exchange_fees.get(exchange_str)
            if not fee_structure:
                raise ModelError(f"Unsupported exchange: {exchange_str}")
            
            # Get base fee rate
            base_fee = fee_structure.maker_fee if is_maker else fee_structure.taker_fee
            
            # Apply volume discounts
            applied_fee = base_fee
            for threshold, discount in sorted(fee_structure.volume_thresholds.items(), reverse=True):
                if notional_value >= threshold:
                    applied_fee = discount
                    break
                    
            # Apply tier multiplier
            tier_multiplier = 1.0 - (0.1 * min(fee_tier - 1, 3))
            final_fee = applied_fee * tier_multiplier
            
            self.logger.debug(
                f"Fee calculation: {notional_value=}, {exchange_str=}, {is_maker=}, "
                f"result={final_fee * notional_value:.4f}"
            )
            
            return final_fee * notional_value
            
        except Exception as e:
            self.logger.error(f"Fee calculation failed: {e}", exc_info=True)
            raise ModelError(f"Fee calculation error: {e}") from e
            
        
            
    def _load_okx_fee_schedule(self) -> FeeStructure:
        """OKX fee schedule as of 2023"""
        return FeeStructure(
            maker_fee=0.0008,  # 0.08%
            taker_fee=0.0010,  # 0.10%
            volume_thresholds={
                10_000_000: 0.0006,  # $10M+ volume
                1_000_000: 0.0007,
                100_000: 0.00075,
                0: 0.0008  # Default
            }
        )
        
    def _load_binance_fee_schedule(self) -> FeeStructure:
        """Binance fee schedule as of 2023"""
        return FeeStructure(
            maker_fee=0.0002,  # 0.02%
            taker_fee=0.0004,  # 0.04%
            volume_thresholds={
                150_000_000: 0.0001,
                50_000_000: 0.00012,
                5_000_000: 0.00016,
                0: 0.0002
            }
        )
        
    def add_custom_exchange(self, 
                          exchange_name: str,
                          maker_fee: float,
                          taker_fee: float,
                          volume_thresholds: Dict[float, float]):
        """
        Add custom exchange fee schedule.
        
        Args:
            exchange_name: Name of exchange to add
            maker_fee: Base maker fee
            taker_fee: Base taker fee
            volume_thresholds: Dict of {volume: fee} pairs
        """
        self.exchange_fees[exchange_name.upper()] = FeeStructure(
            maker_fee=maker_fee,
            taker_fee=taker_fee,
            volume_thresholds=volume_thresholds
        )