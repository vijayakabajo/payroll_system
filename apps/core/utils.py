from decimal import Decimal
import re


def format_indian_currency(amount):
    """Format a number in Indian currency format with ₹ symbol.
    e.g. 125000 → ₹1,25,000.00
    """
    if amount is None:
        return '₹0.00'
    try:
        amount = Decimal(str(amount))
        is_negative = amount < 0
        amount = abs(amount)
        rupees, paise = divmod(amount * 100, 100)
        rupees = int(rupees)
        paise = int(paise)

        # Indian number format: last 3 digits, then groups of 2
        s = str(rupees)
        if len(s) > 3:
            last_three = s[-3:]
            rest = s[:-3]
            formatted_rest = re.sub(r'(\d)(?=(\d{2})+(?!\d))', r'\1,', rest)
            formatted = f'{formatted_rest},{last_three}'
        else:
            formatted = s

        result = f'₹{formatted}.{paise:02d}'
        return f'-{result}' if is_negative else result
    except (ValueError, TypeError):
        return '₹0.00'


def amount_in_words(amount):
    """Convert amount to Indian English words.
    e.g. 12660 → 'Twelve Thousand Six Hundred Sixty Only'
    """
    try:
        from num2words import num2words
        amount = float(amount)
        rupees = int(amount)
        paise = round((amount - rupees) * 100)
        words = num2words(rupees, lang='en_IN').replace('-', ' ').title()
        if paise > 0:
            paise_words = num2words(paise, lang='en_IN').replace('-', ' ').title()
            return f'{words} And {paise_words} Paise Only'
        return f'{words} Only'
    except Exception:
        return ''


def get_month_choices():
    """Return list of month choices."""
    return [
        ('January', 'January'), ('February', 'February'),
        ('March', 'March'), ('April', 'April'),
        ('May', 'May'), ('June', 'June'),
        ('July', 'July'), ('August', 'August'),
        ('September', 'September'), ('October', 'October'),
        ('November', 'November'), ('December', 'December'),
    ]


MONTH_ORDER = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12,
}
