"""
Supabase Client - Database connection and initialization
"""

import streamlit as st
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)


@st.cache_resource
def get_supabase_client() -> Client:
    """Get cached Supabase client instance."""

    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_ANON_KEY")

    if not url or not key:
        raise ValueError(
            "Supabase credentials not configured in Streamlit secrets."
        )

    return create_client(url, key)


@st.cache_resource
def get_supabase_admin_client() -> Client:
    """Get Supabase admin client with service role key."""

    url = st.secrets.get("SUPABASE_URL")
    service_key = st.secrets.get("SUPABASE_SERVICE_KEY")

    if not url or not service_key:
        raise ValueError(
            "Supabase admin credentials not configured in Streamlit secrets."
        )

    return create_client(url, service_key)


def get_db():
    """Convenience function to get database client."""
    return get_supabase_client()


def execute_query(table: str, operation: str, **kwargs):
    """Execute a database query with error handling."""
    try:
        db = get_db()
        query = db.table(table)

        if operation == "select":
            columns = kwargs.get("columns", "*")
            filters = kwargs.get("filters", {})
            limit = kwargs.get("limit")
            order = kwargs.get("order")

            q = query.select(columns)

            for col, val in filters.items():
                q = q.eq(col, val)

            if order:
                q = q.order(order)
            if limit:
                q = q.limit(limit)

            return q.execute()

        elif operation == "insert":
            return query.insert(kwargs.get("data", {})).execute()

        elif operation == "update":
            q = query.update(kwargs.get("data", {}))
            for col, val in kwargs.get("filters", {}).items():
                q = q.eq(col, val)
            return q.execute()

        elif operation == "upsert":
            return query.upsert(kwargs.get("data", {})).execute()

        elif operation == "delete":
            q = query.delete()
            for col, val in kwargs.get("filters", {}).items():
                q = q.eq(col, val)
            return q.execute()

    except Exception as e:
        logger.error(f"Database error on {table}.{operation}: {e}")
        return None