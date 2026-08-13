import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from src.services.approval_service import (
    get_pending_script_approvals, 
    approve_script_and_render,
    get_pending_video_approvals,
    approve_video
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the AdGen Approval Bot.\n\n"
        "Available commands:\n"
        "/pending - List all pending script approvals\n"
        "/approve_script <run_id> <script_id> - Approve a script for rendering\n"
        "/approve_video <run_id> - Approve a rendered video for final publish"
    )


async def pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching pending approvals...")
    
    # 1. Scripts awaiting approval
    scripts = get_pending_script_approvals()
    if not scripts:
        script_msg = "No scripts currently waiting for approval.\n"
    else:
        script_msg = f"**Pending Script Approvals ({len(scripts)}):**\n"
        for s in scripts:
            script_msg += f"\n--- Client: {s['client_id']} (Run: {s['run_id'][:8]}) ---\n"
            script_msg += f"Variant: {s['variant_type']} | Script ID: {s['script_id'][:8]}\n"
            script_msg += f"Hook: {s['hook_text']}\n"
            script_msg += f"Body:\n{s['body_script'][:200]}...\n"
            script_msg += f"To approve: `/approve_script {s['run_id']} {s['script_id']}`\n"
            
    # 2. Videos awaiting approval
    videos = get_pending_video_approvals()
    if not videos:
        video_msg = "\nNo videos currently waiting for final approval."
    else:
        video_msg = f"\n**Pending Video Approvals ({len(videos)}):**\n"
        for v in videos:
            video_msg += f"- Client: {v['client_id']} (Run: {v['id'][:8]})\n"
            video_msg += f"To approve: `/approve_video {v['id']}`\n"

    await update.message.reply_text(script_msg + video_msg, parse_mode="Markdown")


async def approve_script_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /approve_script <run_id> <script_id>")
        return
        
    run_id = context.args[0]
    script_id = context.args[1]
    
    # Needs config_path, which we can look up from the pending list or just assume crowdwisdom for now
    scripts = get_pending_script_approvals()
    config_path = None
    for s in scripts:
        if str(s["run_id"]) == run_id:
            config_path = s["config_path"]
            break
            
    if not config_path:
        await update.message.reply_text("Error: Could not find config_path for this run_id in pending state.")
        return

    await update.message.reply_text(f"Approving script {script_id[:8]}... Please wait while the Video Agent renders the clip. This will take ~45 seconds.")
    
    try:
        # Call the decoupled service logic (synchronous for now, though it ties up the bot thread)
        local_mp4_path, video_record_id = approve_script_and_render(run_id, script_id, config_path)
        
        await update.message.reply_text(f"Render complete! Video uploaded to Supabase.\nSending inline video preview...")
        
        # Send the actual video file inline
        with open(local_mp4_path, 'rb') as video_file:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video_file)
            
        await update.message.reply_text(f"To finalize and publish this video, type:\n`/approve_video {run_id}`", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"Failed to process approval: {str(e)}")


async def approve_video_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /approve_video <run_id>")
        return
        
    run_id = context.args[0]
    
    try:
        success = approve_video(run_id)
        if success:
            await update.message.reply_text(f"✅ Video for run {run_id[:8]} has been approved and published! Pipeline Completed.")
    except Exception as e:
        await update.message.reply_text(f"Failed to approve video: {str(e)}")


def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found in environment.")
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pending", pending))
    application.add_handler(CommandHandler("approve_script", approve_script_cmd))
    application.add_handler(CommandHandler("approve_video", approve_video_cmd))

    print("Telegram Bot starting... (Press Ctrl+C to stop)")
    application.run_polling()

if __name__ == "__main__":
    main()
