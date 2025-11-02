import io
import os
import tempfile
from typing import List
from datetime import datetime

import pandas as pd
import streamlit as st

from pdf_parser import parse_pdf


st.set_page_config(
    page_title="Credit Card Statement Parser",
    layout="wide",
    page_icon="💳"
)

# Header with styling
st.title("💳 Credit Card Statement PDF Parser")

st.markdown("""
    ### Extract Key Information from Credit Card Statements
    
    **Supported Issuers:** Chase, Bank of America, Citi, American Express, Capital One
    
    **Extracted Data Points:**
    1. 🏦 **Issuer** - Credit card company name
    2. 👤 **Cardholder Name** - Account holder name
    3. 💳 **Card Last 4 Digits** - Last 4 digits of card number
    4. 📅 **Statement Period** - Billing cycle dates
    5. ⏰ **Payment Due Date** - When payment is due
    6. 💰 **New Balance** - Total amount due
    
    ---
""")

uploaded_files = st.file_uploader(
    "📁 Upload one or more PDF statements", 
    type=["pdf"], 
    accept_multiple_files=True,
    help="Select one or more credit card statement PDFs from your computer"
)

if uploaded_files:
    results = []
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_files = len(uploaded_files)
    
    for idx, uploaded in enumerate(uploaded_files):
        status_text.text(f"Processing {idx + 1}/{total_files}: {uploaded.name}")
        progress_bar.progress((idx + 1) / total_files)
        
        # write to temp file because pdfplumber expects a path or file-like
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name

            parsed = parse_pdf(tmp_path)
            parsed["filename"] = uploaded.name
            parsed["status"] = "✅ Success"
            results.append(parsed)
        except Exception as e:
            results.append({
                "filename": uploaded.name,
                "issuer": None,
                "cardholder_name": None,
                "card_last4": None,
                "statement_period": None,
                "payment_due_date": None,
                "new_balance": None,
                "status": "❌ Error",
                "error": str(e),
            })
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
    
    status_text.text("✅ Processing complete!")
    progress_bar.empty()

    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Summary statistics
    st.subheader("📊 Processing Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Files", len(results))
    with col2:
        success_count = sum(1 for r in results if "error" not in r or not r["error"])
        st.metric("Successfully Parsed", success_count)
    with col3:
        error_count = sum(1 for r in results if "error" in r and r["error"])
        st.metric("Errors", error_count)
    with col4:
        unique_issuers = df["issuer"].nunique()
        st.metric("Unique Issuers", unique_issuers)
    
    st.markdown("---")
    
    # Display results
    st.subheader("📋 Parsed Results")
    
    # Reorder columns for better display
    display_columns = ["status", "filename", "issuer", "cardholder_name", "card_last4", 
                      "statement_period", "payment_due_date", "new_balance"]
    available_columns = [col for col in display_columns if col in df.columns]
    if "error" in df.columns:
        available_columns.append("error")
    
    df_display = df[available_columns]
    
    # Style the dataframe
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )
    
    # Download options
    st.markdown("---")
    st.subheader("💾 Download Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download as CSV",
            data=csv,
            file_name=f"credit_card_statements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON download
        json_str = df.to_json(orient="records", indent=2)
        st.download_button(
            "📥 Download as JSON",
            data=json_str,
            file_name=f"credit_card_statements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Detailed view
    st.markdown("---")
    st.subheader("🔍 Detailed View")
    
    for idx, row in enumerate(results):
        # Color code based on success/error
        if "error" in row and row["error"]:
            icon = "❌"
            color = "red"
        else:
            icon = "✅"
            color = "green"
        
        with st.expander(f"{icon} {row.get('filename', f'File {idx + 1}')}"):
            if "error" in row and row["error"]:
                st.error(f"**Error:** {row['error']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🏦 Issuer:**", row.get("issuer", "Not detected"))
                st.write("**👤 Cardholder:**", row.get("cardholder_name", "Not found"))
                st.write("**💳 Card Last 4:**", row.get("card_last4", "Not found"))
            
            with col2:
                st.write("**📅 Statement Period:**", row.get("statement_period", "Not found"))
                st.write("**⏰ Payment Due:**", row.get("payment_due_date", "Not found"))
                st.write("**💰 New Balance:**", row.get("new_balance", "Not found"))

else:
    st.info("👆 Upload one or more PDF credit card statements to begin parsing.")
    
    # Add some helpful information
    with st.expander("ℹ️ How to use this tool"):
        st.markdown("""
        ### Instructions:
        1. **Gather your statements**: Collect credit card statement PDFs from any of the supported issuers
        2. **Upload files**: Click the upload button above and select one or more PDF files
        3. **Wait for processing**: The app will automatically extract key information from each statement
        4. **Review results**: Check the parsed data in the table and detailed views
        5. **Download**: Export your results as CSV or JSON for further analysis
        
        ### Privacy Note:
        - All processing happens locally on your machine
        - No data is sent to external servers
        - Files are temporarily stored during processing and immediately deleted
        - Keep your statements confidential and delete exports when done
        
        ### Troubleshooting:
        - If a statement fails to parse, try checking if it's a valid PDF
        - Some statements may have non-standard formats that require manual review
        - Ensure the PDF is not password-protected or corrupted
        """)
