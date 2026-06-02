"""
Supabase Client - Database connection and initialization
"""

import streamlit as st
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
import logging

logger = logging.getLogger(__name__)


@st.cache_resource
def get_supabase_client() -> Client:
    """Get cached Supabase client instance."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise ValueError(
            "Supabase credentials not configured. "
            "Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file."
        )
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


@st.cache_resource
def get_supabase_admin_client() -> Client:
    """Get Supabase admin client with service role key."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError("Supabase admin credentials not configured.")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_db():
    """Convenience function to get database client."""
    return get_supabase_client()


def execute_query(table: str, operation: str, **kwargs):
    """
    Execute a database query with error handling.
    
    Args:
        table: Table name
        operation: Operation type (select, insert, update, delete, upsert)
        **kwargs: Query parameters
    
    Returns:
        Query result or None on error
    """
    try:
        db = get_db()
        query = db.table(table)
        
        if operation == "select":
            columns = kwargs.get("columns", "*")
            filters = kwargs.get("filters", {})
            limit = kwargs.get("limit", None)
            order = kwargs.get("order", None)
            
            q = query.select(columns)
            for col, val in filters.items():
                q = q.eq(col, val)
            if order:
                q = q.order(order)
            if limit:
                q = q.limit(limit)
            return q.execute()
        
        elif operation == "insert":
            data = kwargs.get("data", {})
            return query.insert(data).execute()
        
        elif operation == "update":
            data = kwargs.get("data", {})
            filters = kwargs.get("filters", {})
            q = query.update(data)
            for col, val in filters.items():
                q = q.eq(col, val)
            return q.execute()
        
        elif operation == "upsert":
            data = kwargs.get("data", {})
            return query.upsert(data).execute()
        
        elif operation == "delete":
            filters = kwargs.get("filters", {})
            q = query.delete()
            for col, val in filters.items():
                q = q.eq(col, val)
            return q.execute()
        
    except Exception as e:
        logger.error(f"Database error on {table}.{operation}: {e}")
        return None