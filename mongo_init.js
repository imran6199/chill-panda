// Initialize MongoDB with collections
db = db.getSiblingDB('chillpanda_db');

// Create collections
db.createCollection('chat_history');
db.createCollection('user_sessions');

// Create indexes
db.chat_history.createIndex({ session_id: 1, timestamp: -1 });
db.chat_history.createIndex({ user_id: 1 });
db.user_sessions.createIndex({ session_id: 1 }, { unique: true });
db.user_sessions.createIndex({ user_id: 1 });
db.user_sessions.createIndex({ last_activity: -1 });

print('✅ MongoDB initialized for Chill Panda');