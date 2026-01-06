"""
Cohort Analysis Module
Core logic for calculating cohort metrics from order data.
"""

import pandas as pd
import io
from typing import Tuple, Optional


def load_and_validate_data(file) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Load CSV file and validate required columns.

    Args:
        file: Uploaded file object or file path

    Returns:
        Tuple of (DataFrame, error_message). If successful, error_message is None.
    """
    required_columns = {'order_date', 'customer_id', 'order_amount'}

    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        # Check for required columns
        missing_cols = required_columns - set(df.columns)
        if missing_cols:
            return None, f"Missing required columns: {', '.join(missing_cols)}"

        # Convert order_date to datetime
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        if df['order_date'].isna().any():
            invalid_count = df['order_date'].isna().sum()
            return None, f"Found {invalid_count} rows with invalid dates"

        # Convert order_amount to numeric
        df['order_amount'] = pd.to_numeric(df['order_amount'], errors='coerce')
        if df['order_amount'].isna().any():
            invalid_count = df['order_amount'].isna().sum()
            return None, f"Found {invalid_count} rows with invalid order amounts"

        # Ensure customer_ID is string
        df['customer_id'] = df['customer_id'].astype(str)

        return df, None

    except Exception as e:
        return None, f"Error reading file: {str(e)}"


def calculate_cohorts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign each customer to their cohort based on first purchase month.

    Args:
        df: DataFrame with order_date, customer_id, order_amount

    Returns:
        DataFrame with added cohort_month and order_month columns
    """
    df = df.copy()

    # Get each customer's first order date (cohort)
    customer_cohorts = df.groupby('customer_id')['order_date'].min().reset_index()
    customer_cohorts.columns = ['customer_id', 'cohort_date']
    customer_cohorts['cohort_month'] = customer_cohorts['cohort_date'].dt.to_period('M')

    # Merge cohort info back to main df
    df = df.merge(customer_cohorts[['customer_id', 'cohort_month']], on='customer_id')

    # Add order month
    df['order_month'] = df['order_date'].dt.to_period('M')

    # Calculate months since cohort (cohort index)
    df['cohort_index'] = (df['order_month'] - df['cohort_month']).apply(lambda x: x.n)

    return df


def build_retention_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build cohort retention table showing % of customers returning each month.

    Args:
        df: DataFrame with cohort data (from calculate_cohorts)

    Returns:
        DataFrame with cohort months as rows and period index as columns
    """
    # Count unique customers per cohort per period
    cohort_data = df.groupby(['cohort_month', 'cohort_index'])['customer_id'].nunique().reset_index()
    cohort_data.columns = ['cohort_month', 'cohort_index', 'customers']

    # Pivot to matrix form
    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='customers')

    # Get cohort sizes (month 0)
    cohort_sizes = cohort_pivot[0]

    # Calculate retention percentages
    retention_table = cohort_pivot.divide(cohort_sizes, axis=0) * 100

    # Round to 1 decimal place
    retention_table = retention_table.round(1)

    # Rename columns to Month 0, Month 1, etc.
    retention_table.columns = [f'Month {i}' for i in retention_table.columns]
    retention_table.index = retention_table.index.astype(str)

    return retention_table


def build_revenue_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build cohort revenue table showing total revenue per cohort per month.

    Args:
        df: DataFrame with cohort data (from calculate_cohorts)

    Returns:
        DataFrame with cohort months as rows and period index as columns
    """
    # Sum revenue per cohort per period
    cohort_data = df.groupby(['cohort_month', 'cohort_index'])['order_amount'].sum().reset_index()
    cohort_data.columns = ['cohort_month', 'cohort_index', 'revenue']

    # Pivot to matrix form
    revenue_table = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='revenue')

    # Round to 2 decimal places
    revenue_table = revenue_table.round(2)

    # Rename columns
    revenue_table.columns = [f'Month {i}' for i in revenue_table.columns]
    revenue_table.index = revenue_table.index.astype(str)

    return revenue_table


def build_customer_count_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build cohort customer count table showing unique customers per cohort per month.

    Args:
        df: DataFrame with cohort data (from calculate_cohorts)

    Returns:
        DataFrame with cohort months as rows and period index as columns
    """
    # Count unique customers per cohort per period
    cohort_data = df.groupby(['cohort_month', 'cohort_index'])['customer_id'].nunique().reset_index()
    cohort_data.columns = ['cohort_month', 'cohort_index', 'customers']

    # Pivot to matrix form
    customer_table = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='customers')

    # Rename columns
    customer_table.columns = [f'Month {i}' for i in customer_table.columns]
    customer_table.index = customer_table.index.astype(str)

    return customer_table


def build_revenue_retention_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build cohort revenue retention table showing percentage of Month 0 revenue retained.

    Args:
        df: DataFrame with cohort data (from calculate_cohorts)

    Returns:
        DataFrame with cohort months as rows and period index as columns (percentages)
    """
    # Sum revenue per cohort per period
    cohort_data = df.groupby(['cohort_month', 'cohort_index'])['order_amount'].sum().reset_index()
    cohort_data.columns = ['cohort_month', 'cohort_index', 'revenue']

    # Pivot to matrix form
    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='revenue')

    # Get base revenue (month 0)
    base_revenue = cohort_pivot[0]

    # Calculate retention percentages
    revenue_retention = cohort_pivot.divide(base_revenue, axis=0) * 100

    # Round to 1 decimal place
    revenue_retention = revenue_retention.round(1)

    # Rename columns
    revenue_retention.columns = [f'Month {i}' for i in revenue_retention.columns]
    revenue_retention.index = revenue_retention.index.astype(str)

    return revenue_retention


def get_cohort_summary(df: pd.DataFrame) -> dict:
    """
    Get summary statistics about the cohort data.

    Args:
        df: Original DataFrame with order data

    Returns:
        Dictionary with summary statistics
    """
    return {
        'total_orders': len(df),
        'unique_customers': df['customer_id'].nunique(),
        'total_revenue': df['order_amount'].sum(),
        'date_range': f"{df['order_date'].min().strftime('%Y-%m-%d')} to {df['order_date'].max().strftime('%Y-%m-%d')}",
        'num_cohorts': df['cohort_month'].nunique() if 'cohort_month' in df.columns else 0
    }


def style_retention_table(df: pd.DataFrame):
    """
    Apply heatmap styling to retention table.
    Green = high retention, Red = low retention
    """
    return df.style.background_gradient(
        cmap='RdYlGn',
        vmin=0,
        vmax=100,
        axis=None
    ).format('{:.1f}%', na_rep='-')


def style_revenue_table(df: pd.DataFrame):
    """
    Apply heatmap styling to revenue table.
    """
    return df.style.background_gradient(
        cmap='Blues',
        axis=None
    ).format('${:,.0f}', na_rep='-')


def style_customer_table(df: pd.DataFrame):
    """
    Apply heatmap styling to customer count table.
    """
    return df.style.background_gradient(
        cmap='Purples',
        axis=None
    ).format('{:.0f}', na_rep='-')


def style_revenue_retention_table(df: pd.DataFrame):
    """
    Apply heatmap styling to revenue retention table.
    Green = high retention, Red = low retention
    """
    return df.style.background_gradient(
        cmap='RdYlGn',
        vmin=0,
        vmax=100,
        axis=None
    ).format('{:.1f}%', na_rep='-')


def export_to_excel(retention_df: pd.DataFrame, revenue_df: pd.DataFrame,
                    customer_df: pd.DataFrame, revenue_retention_df: pd.DataFrame = None) -> bytes:
    """
    Export all cohort tables to a single Excel file with multiple sheets.

    Returns:
        Bytes of the Excel file
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        retention_df.to_excel(writer, sheet_name='Customer Retention %')
        customer_df.to_excel(writer, sheet_name='Customer Count')
        if revenue_retention_df is not None:
            revenue_retention_df.to_excel(writer, sheet_name='Revenue Retention %')
        revenue_df.to_excel(writer, sheet_name='Revenue $')
    output.seek(0)
    return output.getvalue()


def get_advanced_metrics(df: pd.DataFrame) -> dict:
    """
    Calculate advanced business metrics.

    Args:
        df: DataFrame with cohort data (from calculate_cohorts)

    Returns:
        Dictionary with advanced metrics
    """
    total_revenue = df['order_amount'].sum()
    total_orders = len(df)
    unique_customers = df['customer_id'].nunique()

    # Orders per customer
    orders_per_customer = df.groupby('customer_id').size()
    repeat_customers = (orders_per_customer > 1).sum()

    # Calculate metrics
    ltv = total_revenue / unique_customers if unique_customers > 0 else 0
    aov = total_revenue / total_orders if total_orders > 0 else 0
    repeat_rate = (repeat_customers / unique_customers * 100) if unique_customers > 0 else 0
    avg_orders_per_customer = total_orders / unique_customers if unique_customers > 0 else 0

    return {
        'ltv': ltv,
        'aov': aov,
        'repeat_rate': repeat_rate,
        'avg_orders_per_customer': avg_orders_per_customer,
        'repeat_customers': repeat_customers,
        'one_time_customers': unique_customers - repeat_customers
    }


def get_cohort_sizes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get the size of each cohort (new customers per month).

    Args:
        df: DataFrame with cohort data

    Returns:
        DataFrame with cohort month and customer count
    """
    cohort_sizes = df.groupby('cohort_month')['customer_id'].nunique().reset_index()
    cohort_sizes.columns = ['cohort_month', 'new_customers']
    cohort_sizes['cohort_month'] = cohort_sizes['cohort_month'].astype(str)
    return cohort_sizes


def get_retention_curve(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate average retention rate across all cohorts by month index.

    Args:
        df: DataFrame with cohort data

    Returns:
        DataFrame with month index and average retention
    """
    # Count unique customers per cohort per period
    cohort_data = df.groupby(['cohort_month', 'cohort_index'])['customer_id'].nunique().reset_index()
    cohort_data.columns = ['cohort_month', 'cohort_index', 'customers']

    # Pivot to get cohort sizes
    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='customers')

    # Get cohort sizes (month 0)
    cohort_sizes = cohort_pivot[0]

    # Calculate retention percentages
    retention_pct = cohort_pivot.divide(cohort_sizes, axis=0) * 100

    # Average across cohorts for each month index
    avg_retention = retention_pct.mean().reset_index()
    avg_retention.columns = ['month', 'retention']
    avg_retention['month'] = avg_retention['month'].astype(int)

    return avg_retention


def generate_insights(df: pd.DataFrame, retention_table: pd.DataFrame,
                      metrics: dict = None, cohort_sizes: pd.DataFrame = None) -> list:
    """
    Generate automatic insights from the cohort data.

    Args:
        df: DataFrame with cohort data
        retention_table: Retention table DataFrame
        metrics: Pre-calculated metrics (optional, avoids redundant calculation)
        cohort_sizes: Pre-calculated cohort sizes (optional)

    Returns:
        List of insight dictionaries
    """
    insights = []

    try:
        # Use provided metrics or calculate if not provided
        if metrics is None:
            metrics = get_advanced_metrics(df)
        if cohort_sizes is None:
            cohort_sizes = get_cohort_sizes(df)

        # Insight 1: Repeat purchase rate
        if metrics['repeat_rate'] >= 30:
            insights.append({
                'type': 'positive',
                'title': 'Strong repeat purchases',
                'text': f"{metrics['repeat_rate']:.1f}% of customers have made more than one purchase."
            })
        elif metrics['repeat_rate'] < 15:
            insights.append({
                'type': 'warning',
                'title': 'Low repeat rate',
                'text': f"Only {metrics['repeat_rate']:.1f}% of customers return. Consider retention strategies."
            })

        # Insight 2: Best performing cohort (Month 1 retention)
        if 'Month 1' in retention_table.columns:
            month1_retention = retention_table['Month 1'].dropna()
            if len(month1_retention) > 1:  # Need at least 2 cohorts to compare
                best_cohort = month1_retention.idxmax()
                best_retention = month1_retention.max()
                avg_retention = month1_retention.mean()

                # Prevent division by zero
                if avg_retention > 0 and best_retention > avg_retention * 1.2:
                    insights.append({
                        'type': 'positive',
                        'title': 'Top performing cohort',
                        'text': f"{best_cohort} cohort has {best_retention:.1f}% Month 1 retention, {((best_retention/avg_retention)-1)*100:.0f}% above average."
                    })

                # Worst cohort
                worst_cohort = month1_retention.idxmin()
                worst_retention = month1_retention.min()
                if avg_retention > 0 and worst_retention < avg_retention * 0.8:
                    insights.append({
                        'type': 'warning',
                        'title': 'Underperforming cohort',
                        'text': f"{worst_cohort} cohort has only {worst_retention:.1f}% Month 1 retention."
                    })

        # Insight 3: Cohort size trend
        if len(cohort_sizes) >= 6:  # Need enough cohorts to compare trends
            recent_avg = cohort_sizes['new_customers'].tail(3).mean()
            older_avg = cohort_sizes['new_customers'].head(3).mean()

            # Prevent division by zero
            if older_avg > 0:
                if recent_avg > older_avg * 1.2:
                    growth_pct = ((recent_avg / older_avg) - 1) * 100
                    insights.append({
                        'type': 'positive',
                        'title': 'Growing customer acquisition',
                        'text': f"Recent cohorts are {growth_pct:.0f}% larger than earlier ones."
                    })
                elif recent_avg < older_avg * 0.8:
                    decline_pct = (1 - (recent_avg / older_avg)) * 100
                    insights.append({
                        'type': 'warning',
                        'title': 'Declining acquisition',
                        'text': f"Recent cohorts are {decline_pct:.0f}% smaller than earlier ones."
                    })

        # Insight 4: Lifetime revenue insight
        if metrics['ltv'] > 0:
            insights.append({
                'type': 'info',
                'title': 'Lifetime revenue',
                'text': f"Average customer generates ${metrics['ltv']:.2f} in revenue over their lifetime."
            })

        # Insight 5: Purchase frequency
        if metrics['avg_orders_per_customer'] > 0:
            insights.append({
                'type': 'info',
                'title': 'Purchase frequency',
                'text': f"Customers place an average of {metrics['avg_orders_per_customer']:.1f} orders each."
            })

        # Insight 6: Month 2+ retention (stickiness)
        if 'Month 2' in retention_table.columns:
            month2_data = retention_table['Month 2'].dropna()
            if len(month2_data) > 0:
                month2_avg = month2_data.mean()
                if month2_avg >= 20:
                    insights.append({
                        'type': 'positive',
                        'title': 'Good long-term retention',
                        'text': f"Average {month2_avg:.1f}% of customers are still active by Month 2."
                    })

    except Exception:
        # If insight generation fails, return empty list rather than crashing
        pass

    return insights[:6]  # Return top 6 insights
