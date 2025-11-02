"""
Mock Credit Card Statement Generator

This script generates realistic-looking credit card statement PDFs for testing
the PDF parser without using real financial data.

Supports all 5 issuers: Chase, Bank of America, Citi, American Express, Capital One

Usage: python generate_mock_statements.py
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas
import random
from datetime import datetime, timedelta
import os


class MockStatementGenerator:
    """Generates mock credit card statements for testing."""
    
    ISSUERS = {
        'chase': 'Chase',
        'bofa': 'Bank of America',
        'citi': 'Citi',
        'amex': 'American Express',
        'capital_one': 'Capital One'
    }
    
    SAMPLE_NAMES = [
        'John Doe', 'Jane Smith', 'Michael Johnson', 'Emily Davis',
        'Robert Wilson', 'Sarah Martinez', 'David Anderson', 'Jennifer Taylor'
    ]
    
    SAMPLE_MERCHANTS = [
        'Amazon.com', 'Walmart', 'Target', 'Starbucks', 'Shell Gas Station',
        'McDonald\'s', 'Home Depot', 'CVS Pharmacy', 'Uber', 'Netflix',
        'AT&T', 'Whole Foods', 'Best Buy', 'Apple Store', 'Costco'
    ]
    
    def __init__(self, output_dir='mock_statements'):
        """Initialize the generator."""
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_transactions(self, num_transactions=15):
        """Generate random transactions."""
        transactions = []
        current_date = datetime.now() - timedelta(days=random.randint(5, 30))
        
        for _ in range(num_transactions):
            merchant = random.choice(self.SAMPLE_MERCHANTS)
            amount = round(random.uniform(5.99, 299.99), 2)
            transactions.append({
                'date': current_date.strftime('%m/%d/%Y'),
                'merchant': merchant,
                'amount': amount
            })
            current_date -= timedelta(days=random.randint(1, 3))
        
        return transactions
    
    def generate_chase_statement(self, filename='chase_statement.pdf'):
        """Generate a Chase-style statement."""
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "Chase")
        
        # Account info
        cardholder_name = random.choice(self.SAMPLE_NAMES)
        card_last4 = f"{random.randint(1000, 9999)}"
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 80, f"Account holder: {cardholder_name}")
        c.drawString(50, height - 95, f"Account ending in {card_last4}")
        
        # Statement period
        end_date = datetime.now() - timedelta(days=5)
        start_date = end_date - timedelta(days=30)
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 130, "Statement Details")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 145, f"Statement period: {start_date.strftime('%m/%d/%Y')} - {end_date.strftime('%m/%d/%Y')}")
        
        due_date = end_date + timedelta(days=25)
        c.drawString(50, height - 160, f"Payment due date: {due_date.strftime('%m/%d/%Y')}")
        
        # Balance
        transactions = self.generate_transactions()
        total_balance = sum(t['amount'] for t in transactions)
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 190, f"New balance: ${total_balance:,.2f}")
        c.drawString(50, height - 210, f"Total due: ${total_balance:,.2f}")
        
        # Transactions section
        y_position = height - 250
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y_position, "Transactions")
        
        y_position -= 20
        c.setFont("Helvetica", 9)
        c.drawString(50, y_position, "Date")
        c.drawString(150, y_position, "Description")
        c.drawString(400, y_position, "Amount")
        
        y_position -= 5
        c.line(50, y_position, width - 50, y_position)
        y_position -= 15
        
        for trans in transactions[:10]:  # Show first 10 transactions
            if y_position < 100:
                break
            c.setFont("Helvetica", 8)
            c.drawString(50, y_position, trans['date'])
            c.drawString(150, y_position, trans['merchant'])
            c.drawString(400, y_position, f"${trans['amount']:.2f}")
            y_position -= 15
        
        c.save()
        return filepath
    
    def generate_bofa_statement(self, filename='bofa_statement.pdf'):
        """Generate a Bank of America-style statement."""
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height - 50, "Bank of America")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 65, "Credit Card Statement")
        
        # Account info
        cardholder_name = random.choice(self.SAMPLE_NAMES)
        card_last4 = f"{random.randint(1000, 9999)}"
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 100, f"Statement for: {cardholder_name}")
        c.drawString(50, height - 115, f"Account number ending in: {card_last4}")
        
        # Statement period
        end_date = datetime.now() - timedelta(days=5)
        start_date = end_date - timedelta(days=30)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 145, "Billing Period")
        c.setFont("Helvetica", 9)
        c.drawString(50, height - 160, f"From {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}")
        
        due_date = end_date + timedelta(days=25)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 185, f"Payment Due Date: {due_date.strftime('%m/%d/%Y')}")
        
        # Balance
        transactions = self.generate_transactions()
        total_balance = sum(t['amount'] for t in transactions)
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 215, "Account Summary")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 235, f"New account balance: ${total_balance:,.2f}")
        c.drawString(50, height - 250, f"Current balance: ${total_balance:,.2f}")
        
        # Transactions
        y_position = height - 290
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y_position, "Transaction Details")
        
        y_position -= 20
        c.setFont("Helvetica-Bold", 8)
        c.drawString(50, y_position, "Date")
        c.drawString(150, y_position, "Merchant")
        c.drawString(400, y_position, "Amount")
        
        y_position -= 15
        for trans in transactions[:10]:
            if y_position < 100:
                break
            c.setFont("Helvetica", 8)
            c.drawString(50, y_position, trans['date'])
            c.drawString(150, y_position, trans['merchant'])
            c.drawString(400, y_position, f"${trans['amount']:.2f}")
            y_position -= 15
        
        c.save()
        return filepath
    
    def generate_citi_statement(self, filename='citi_statement.pdf'):
        """Generate a Citi-style statement."""
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 22)
        c.drawString(50, height - 50, "Citi")
        
        # Account info
        cardholder_name = random.choice(self.SAMPLE_NAMES)
        card_last4 = f"{random.randint(1000, 9999)}"
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 85, f"Cardholder: {cardholder_name}")
        c.drawString(50, height - 100, f"Card ending in {card_last4}")
        
        # Statement period
        end_date = datetime.now() - timedelta(days=5)
        start_date = end_date - timedelta(days=30)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 130, "Statement Closing Date")
        c.setFont("Helvetica", 9)
        c.drawString(50, height - 145, end_date.strftime('%m/%d/%Y'))
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 170, "Statement Period")
        c.setFont("Helvetica", 9)
        c.drawString(50, height - 185, f"{start_date.strftime('%m/%d/%Y')} - {end_date.strftime('%m/%d/%Y')}")
        
        due_date = end_date + timedelta(days=25)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 210, f"Payment due date: {due_date.strftime('%m/%d/%Y')}")
        
        # Balance
        transactions = self.generate_transactions()
        total_balance = sum(t['amount'] for t in transactions)
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 245, f"New balance: ${total_balance:,.2f}")
        
        # Transactions
        y_position = height - 285
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y_position, "Purchases and Adjustments")
        
        y_position -= 20
        c.setFont("Helvetica", 8)
        for trans in transactions[:12]:
            if y_position < 100:
                break
            c.drawString(50, y_position, trans['date'])
            c.drawString(140, y_position, trans['merchant'])
            c.drawString(400, y_position, f"${trans['amount']:.2f}")
            y_position -= 15
        
        c.save()
        return filepath
    
    def generate_amex_statement(self, filename='amex_statement.pdf'):
        """Generate an American Express-style statement."""
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "American Express")
        
        # Account info
        cardholder_name = random.choice(self.SAMPLE_NAMES)
        card_last4 = f"{random.randint(1000, 9999)}"
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 85, f"Member Name: {cardholder_name}")
        c.drawString(50, height - 100, f"Account ending in {card_last4}")
        
        # Statement period
        end_date = datetime.now() - timedelta(days=5)
        start_date = end_date - timedelta(days=30)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 130, "Statement Period")
        c.setFont("Helvetica", 9)
        c.drawString(50, height - 145, f"{start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}")
        
        due_date = end_date + timedelta(days=25)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 170, f"Payment due: {due_date.strftime('%m/%d/%Y')}")
        
        # Balance
        transactions = self.generate_transactions()
        total_balance = sum(t['amount'] for t in transactions)
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 200, "Payment Information")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 220, f"New balance: ${total_balance:,.2f}")
        c.drawString(50, height - 235, f"Total due: ${total_balance:,.2f}")
        
        # Transactions
        y_position = height - 270
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y_position, "Charges")
        
        y_position -= 20
        c.setFont("Helvetica", 8)
        for trans in transactions[:11]:
            if y_position < 100:
                break
            c.drawString(50, y_position, trans['date'])
            c.drawString(140, y_position, trans['merchant'])
            c.drawString(400, y_position, f"${trans['amount']:.2f}")
            y_position -= 15
        
        c.save()
        return filepath
    
    def generate_capital_one_statement(self, filename='capital_one_statement.pdf'):
        """Generate a Capital One-style statement."""
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "Capital One")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 65, "Credit Card Statement")
        
        # Account info
        cardholder_name = random.choice(self.SAMPLE_NAMES)
        card_last4 = f"{random.randint(1000, 9999)}"
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 100, f"Account holder: {cardholder_name}")
        c.drawString(50, height - 115, f"Account ending in {card_last4}")
        
        # Statement period
        end_date = datetime.now() - timedelta(days=5)
        start_date = end_date - timedelta(days=30)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 145, "Billing Cycle")
        c.setFont("Helvetica", 9)
        c.drawString(50, height - 160, f"{start_date.strftime('%m/%d/%Y')} - {end_date.strftime('%m/%d/%Y')}")
        
        due_date = end_date + timedelta(days=25)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 185, f"Pay by: {due_date.strftime('%m/%d/%Y')}")
        
        # Balance
        transactions = self.generate_transactions()
        total_balance = sum(t['amount'] for t in transactions)
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 215, "Account Summary")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 235, f"New balance: ${total_balance:,.2f}")
        c.drawString(50, height - 250, f"Amount due: ${total_balance:,.2f}")
        
        # Transactions
        y_position = height - 285
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y_position, "Transactions")
        
        y_position -= 20
        c.setFont("Helvetica", 8)
        for trans in transactions[:12]:
            if y_position < 100:
                break
            c.drawString(50, y_position, trans['date'])
            c.drawString(140, y_position, trans['merchant'])
            c.drawString(400, y_position, f"${trans['amount']:.2f}")
            y_position -= 15
        
        c.save()
        return filepath
    
    def generate_all_statements(self, num_each=2):
        """Generate multiple statements for each issuer."""
        generated_files = []
        
        print("Generating mock credit card statements...\n")
        
        for i in range(num_each):
            # Chase
            filename = f"chase_statement_{i+1}.pdf"
            filepath = self.generate_chase_statement(filename)
            generated_files.append(filepath)
            print(f"Generated: {filename}")
            
            # Bank of America
            filename = f"bofa_statement_{i+1}.pdf"
            filepath = self.generate_bofa_statement(filename)
            generated_files.append(filepath)
            print(f"Generated: {filename}")
            
            # Citi
            filename = f"citi_statement_{i+1}.pdf"
            filepath = self.generate_citi_statement(filename)
            generated_files.append(filepath)
            print(f"Generated: {filename}")
            
            # American Express
            filename = f"amex_statement_{i+1}.pdf"
            filepath = self.generate_amex_statement(filename)
            generated_files.append(filepath)
            print(f"Generated: {filename}")
            
            # Capital One
            filename = f"capital_one_statement_{i+1}.pdf"
            filepath = self.generate_capital_one_statement(filename)
            generated_files.append(filepath)
            print(f"Generated: {filename}")
        
        print(f"\nSuccessfully generated {len(generated_files)} mock statements")
        print(f"Location: {os.path.abspath(self.output_dir)}")
        
        return generated_files


def main():
    """Main function to generate mock statements."""
    print("="*60)
    print("Mock Credit Card Statement Generator")
    print("="*60)
    print()
    
    # Create generator
    generator = MockStatementGenerator()
    
    # Generate 2 statements for each issuer (10 total)
    files = generator.generate_all_statements(num_each=2)


if __name__ == "__main__":
    main()
