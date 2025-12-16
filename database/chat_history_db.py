"""
Chat History Database Module
Handles persistent storage of conversations and messages
Uses connection pooling for optimal performance
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from config import DB_CONFIG
import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection pool for chat history operations
_chat_pool = None
_pool_lock = threading.Lock()


def get_chat_pool():
    """Get or create connection pool for chat history operations"""
    global _chat_pool
    if _chat_pool is None:
        with _pool_lock:
            if _chat_pool is None:
                try:
                    _chat_pool = pool.ThreadedConnectionPool(
                        minconn=2,
                        maxconn=10,
                        host=DB_CONFIG['host'],
                        port=DB_CONFIG['port'],
                        database=DB_CONFIG['database'],
                        user=DB_CONFIG['user'],
                        password=DB_CONFIG['password']
                    )
                    logger.info("Chat history connection pool created")
                except Exception as e:
                    logger.error(f"Failed to create connection pool: {e}")
                    raise
    return _chat_pool


def get_connection():
    """Get a connection from the pool"""
    pool = get_chat_pool()
    return pool.getconn()


def return_connection(conn):
    """Return a connection to the pool"""
    pool = get_chat_pool()
    pool.putconn(conn)


def create_conversation(title: str, user_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """
    Create a new conversation and return its ID
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            conversation_id = uuid.uuid4()
            # Convert UUIDs to strings for psycopg2
            user_id_str = str(user_id) if user_id else None
            cursor.execute(
                """
                INSERT INTO conversations (id, user_id, title, created_at, updated_at)
                VALUES (%s::uuid, %s::uuid, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id
                """,
                (str(conversation_id), user_id_str, title)
            )
            result = cursor.fetchone()
            conn.commit()
            conversation_id = result[0] if result else conversation_id
            logger.info(f"Created conversation {conversation_id} with title: {title}")
            return conversation_id
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creating conversation: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


def save_message(
    conversation_id: uuid.UUID,
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> uuid.UUID:
    """
    Save a message to the database
    Returns the message ID
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            message_id = uuid.uuid4()
            import json
            metadata_json = json.dumps(metadata) if metadata else '{}'
            
            cursor.execute(
                """
                INSERT INTO messages (id, conversation_id, role, content, metadata, created_at)
                VALUES (%s::uuid, %s::uuid, %s, %s, %s::jsonb, CURRENT_TIMESTAMP)
                RETURNING id
                """,
                (str(message_id), str(conversation_id), role, content, metadata_json)
            )
            conn.commit()
            logger.debug(f"Saved message {message_id} to conversation {conversation_id}")
            return message_id
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error saving message: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


def get_conversations(user_id: Optional[uuid.UUID] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get list of conversations, optionally filtered by user_id
    Returns conversations ordered by updated_at DESC
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if user_id:
                cursor.execute(
                    """
                    SELECT c.id, c.title, c.created_at, c.updated_at,
                           (SELECT content FROM messages 
                            WHERE conversation_id = c.id 
                            ORDER BY created_at DESC LIMIT 1) as last_message_preview
                    FROM conversations c
                    WHERE c.user_id = %s::uuid
                    ORDER BY c.updated_at DESC
                    LIMIT %s
                    """,
                    (str(user_id), limit)
                )
            else:
                # For guest users, get all conversations (in production, you'd want session-based filtering)
                cursor.execute(
                    """
                    SELECT c.id, c.title, c.created_at, c.updated_at,
                           (SELECT content FROM messages 
                            WHERE conversation_id = c.id 
                            ORDER BY created_at DESC LIMIT 1) as last_message_preview
                    FROM conversations c
                    ORDER BY c.updated_at DESC
                    LIMIT %s
                    """,
                    (limit,)
                )
            
            results = cursor.fetchall()
            conversations = []
            for row in results:
                conversations.append({
                    'id': str(row['id']),
                    'title': row['title'],
                    'last_message_preview': row['last_message_preview'][:100] + '...' if row['last_message_preview'] and len(row['last_message_preview']) > 100 else (row['last_message_preview'] or ''),
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                })
            return conversations
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


def get_conversation_messages(conversation_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get messages for a conversation with pagination
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, role, content, metadata, created_at
                FROM messages
                WHERE conversation_id = %s::uuid
                ORDER BY created_at ASC
                LIMIT %s OFFSET %s
                """,
                (str(conversation_id), limit, offset)
            )
            
            results = cursor.fetchall()
            messages = []
            for row in results:
                import json
                metadata = row['metadata'] if row['metadata'] else {}
                messages.append({
                    'id': str(row['id']),
                    'role': row['role'],
                    'content': row['content'],
                    'metadata': metadata if isinstance(metadata, dict) else json.loads(metadata) if metadata else {},
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None
                })
            return messages
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


def delete_conversation(conversation_id: uuid.UUID) -> bool:
    """
    Delete a conversation and all its messages (CASCADE)
    Returns True if successful
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM conversations WHERE id = %s::uuid",
                (str(conversation_id),)
            )
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted conversation {conversation_id}")
            return deleted
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error deleting conversation: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


def generate_conversation_title(first_message: str) -> str:
    """
    Generate a title from the first user message
    Truncate to 50 characters and add ellipsis if needed
    """
    if not first_message:
        return "New Conversation"
    
    # Clean up the message
    title = first_message.strip()
    
    # Remove common question words for cleaner titles
    title = title.replace("How many", "").replace("What", "").replace("When", "").replace("Show me", "").replace("Tell me", "").strip()
    
    # Truncate to 50 characters
    if len(title) > 50:
        title = title[:47] + "..."
    
    # If title is too short after cleaning, use original
    if len(title) < 5:
        title = first_message[:50]
        if len(first_message) > 50:
            title = title[:47] + "..."
    
    return title or "New Conversation"

