import sys
import logging
from pathlib import Path
from datetime import datetime

from core.settings import get_settings


class AuctionFormatter(logging.Formatter):
    """Custom formatter for auction-specific log messages."""

    def format(self, record: logging.LogRecord) -> str:
        """Formats log record with custom styling."""
        if hasattr(record, 'auction_data'):
            return self._format_auction(record)
        return super().format(record)

    def _format_auction(self, record: logging.LogRecord) -> str:
        """Formats auction-specific log records."""
        data = record.auction_data
        lines = [
            f"Auction for {data['supply_id']} (country={data['country']}):"]

        for bidder_id, bid_info in data['bids'].items():
            if not bid_info['bid']:
                lines.append(f"  {bidder_id} - no bid")
            else:
                lines.append(f"  {bidder_id} - price {bid_info['bid']:.2f}")

        if data['winner']:
            lines.append(f"Winner: {data['winner']} ({data['price']:.2f})")
        else:
            lines.append("Winner: none")

        return "\n".join(lines)


def setup_logging() -> None:
    """Configures application logging to stdout and file."""
    settings = get_settings()

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper()))

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = AuctionFormatter(log_format)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    logs_dir = Path("/app/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_filename = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file = logs_dir / log_filename

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, settings.log_level.upper()))
    file_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(getattr(logging, settings.log_level.upper()))


def get_logger(name: str) -> logging.Logger:
    """Returns logger instance for the given name."""
    return logging.getLogger(name)
