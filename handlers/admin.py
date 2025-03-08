from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import admin_required
from database.models import UserModel, MessageModel
import asyncio

class AdminHandler:
    def __init__(self):
        self.user_model = UserModel()
        self.message_model = MessageModel()

    @admin_required
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /broadcast <message>")
            return

        broadcast_message = " ".join(context.args)
        users = list(self.user_model.db.users.find({}, {"user_id": 1}))
        total_users = len(users)
        successful = 0
        failed = []

        status_message = await update.message.reply_text(
            f"🔄 Broadcasting message to {total_users} users..."
        )

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user["user_id"],
                    text=broadcast_message,
                    parse_mode='Markdown'
                )
                successful += 1
                
                if successful % 10 == 0:
                    await status_message.edit_text(
                        f"🔄 Progress: {successful}/{total_users} users..."
                    )
                
                await asyncio.sleep(0.035)
                
            except Exception as e:
                failed.append(user["user_id"])
                print(f"Failed to send broadcast to {user['user_id']}: {str(e)}")

        report = (
            f"✅ Broadcast completed!\n"
            f"📊 Statistics:\n"
            f"- Total users: {total_users}\n"
            f"- Successful: {successful}\n"
            f"- Failed: {len(failed)}"
        )
        
        if failed:
            report += f"\n\n❌ Failed IDs: {', '.join(map(str, failed))}"

        await status_message.edit_text(report)

    @admin_required
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        total_users = self.user_model.db.users.count_documents({})
        new_users_today = self.user_model.db.users.count_documents({
            "created_at": {"$gte": datetime.utcnow() - timedelta(days=1)}
        })
        active_today = self.user_model.db.users.count_documents({
            "last_interaction": {"$gte": datetime.utcnow() - timedelta(days=1)}
        })
        active_week = self.user_model.db.users.count_documents({
            "last_interaction": {"$gte": datetime.utcnow() - timedelta(days=7)}
        })
        
        total_messages = list(self.message_model.db.messages.aggregate([
            {"$project": {"messageCount": {"$size": "$conversation"}}},
            {"$group": {"_id": None, "total": {"$sum": "$messageCount"}}}
        ]))
        message_count = total_messages[0]["total"] if total_messages else 0
        
        personality_stats = self.user_model.db.users.aggregate([
            {"$group": {"_id": "$personality", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
        personality_dist = {stat["_id"]: stat["count"] for stat in personality_stats if stat["_id"]}
        
        stats = (
            "📊 *Bot Statistics Dashboard*\n\n"
            f"👥 *User Stats:*\n"
            f"• Total Users: {total_users:,}\n"
            f"• New Users (24h): {new_users_today:,}\n"
            f"• Active Today: {active_today:,}\n"
            f"• Active This Week: {active_week:,}\n\n"
            f"💬 *Message Stats:*\n"
            f"• Total Messages: {message_count:,}\n"
            f"• Avg Messages/User: {message_count/total_users:.1f}\n\n"
            f"🎭 *Personality Distribution:*\n"
        )
        
        for personality, count in personality_dist.items():
            percentage = (count / total_users) * 100
            emoji = {"friendly": "🤗", "witty": "😎", "expert": "🧠"}.get(personality, "➖")
            stats += f"• {emoji} {personality.title()}: {count:,} ({percentage:.1f}%)\n"

        await update.message.reply_text(stats, parse_mode='Markdown')