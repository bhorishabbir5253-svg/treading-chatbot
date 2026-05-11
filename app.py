import os
from flask import Flask, request, jsonify, render_template_string
from startup import *
from chatbot import load_trading_chatbot
 
app = Flask(__name__)
qa_chain = load_trading_chatbot()
 
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trading Chatbot</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
 
  body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0a0a0a 0%, #0d1117 50%, #0a0f1e 100%);
    min-height: 100vh;
    color: #e0e0e0;
    display: flex;
    flex-direction: row;
    --primary-color: #22c55e;
    --secondary-color: #3b82f6;
    --bg-dark: #0a0a0a;
    --bg-card: rgba(22, 27, 34, 0.8);
    --border-color: rgba(34, 197, 94, 0.2);
  }

  body.light-mode {
    --primary-color: #059669;
    --secondary-color: #1d4ed8;
    --bg-dark: #f3f4f6;
    --bg-card: rgba(255, 255, 255, 0.9);
    --border-color: rgba(5, 150, 105, 0.2);
    background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 50%, #f0fdf4 100%);
    color: #1f2937;
  }

  body.light-mode .bubble.bot { background: rgba(240, 253, 244, 0.9); color: #1f2937; }
  body.light-mode .bubble.user { color: #1f2937; }
  body.light-mode header { background: rgba(255, 255, 255, 0.95); }
  body.light-mode .input-wrapper { background: rgba(255, 255, 255, 0.95); }
  body.light-mode .logo { background: linear-gradient(135deg, #059669, #047857); }
  body.light-mode .send-btn { background: linear-gradient(135deg, #059669, #047857); }

  body.blue-theme --primary-color { --primary-color: #3b82f6; }
  body.blue-theme --primary-color { --border-color: rgba(59, 130, 246, 0.2); }
    background:
      radial-gradient(ellipse at 20% 20%, rgba(34, 197, 94, 0.05) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 80%, rgba(59, 130, 246, 0.05) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
  }
 
  /* Sidebar */
  .sidebar {
    width: 280px;
    background: rgba(15, 17, 23, 0.95);
    backdrop-filter: blur(10px);
    border-right: 1px solid var(--border-color);
    padding: 16px;
    overflow-y: auto;
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 90;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .sidebar.collapsed { display: none; }

  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid var(--border-color);
  }

  .sidebar-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #fff;
  }

  .history-item {
    padding: 10px 12px;
    background: rgba(22, 27, 34, 0.5);
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.75rem;
    color: #6b7280;
    border: 1px solid transparent;
    transition: all 0.2s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .history-item:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    background: rgba(34, 197, 94, 0.05);
  }

  .sidebar-btn {
    width: 100%;
    padding: 10px;
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--primary-color);
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 8px;
    justify-content: center;
  }

  .sidebar-btn:hover {
    background: rgba(34, 197, 94, 0.15);
    border-color: var(--primary-color);
  }

  /* Settings Panel */
  .settings-panel {
    position: fixed;
    right: -350px;
    top: 0;
    width: 350px;
    height: 100vh;
    background: rgba(22, 27, 34, 0.98);
    backdrop-filter: blur(10px);
    border-left: 1px solid var(--border-color);
    padding: 20px;
    overflow-y: auto;
    z-index: 95;
    transition: right 0.3s ease;
  }

  .settings-panel.open { right: 0; }

  .settings-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color);
  }

  .settings-title { font-size: 0.95rem; font-weight: 700; }

  .close-settings { background: none; border: none; color: #fff; cursor: pointer; font-size: 1.2rem; }

  .setting-group {
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
  }

  .setting-label {
    font-size: 0.75rem;
    color: #6b7280;
    margin-bottom: 8px;
    display: block;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .theme-picker {
    display: flex;
    gap: 8px;
  }

  .theme-option {
    flex: 1;
    padding: 8px;
    border: 2px solid transparent;
    border-radius: 6px;
    text-align: center;
    cursor: pointer;
    font-size: 0.7rem;
    transition: all 0.2s;
  }

  .theme-option.active {
    border-color: var(--primary-color);
    background: rgba(34, 197, 94, 0.1);
  }

  /* Command Palette */
  .command-palette {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(4px);
    z-index: 200;
    display: none;
    align-items: flex-start;
    justify-content: center;
    padding-top: 80px;
  }

  .command-palette.open { display: flex; }

  .command-input-wrapper {
    width: 90%;
    max-width: 600px;
    background: rgba(22, 27, 34, 0.95);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  }

  .command-input {
    width: 100%;
    padding: 16px;
    background: transparent;
    border: none;
    color: #fff;
    outline: none;
    font-size: 0.9rem;
  }

  .command-list {
    max-height: 300px;
    overflow-y: auto;
    border-top: 1px solid var(--border-color);
  }

  .command-item {
    padding: 12px 16px;
    cursor: pointer;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    transition: all 0.2s;
  }

  .command-item:hover {
    background: rgba(34, 197, 94, 0.1);
    color: var(--primary-color);
  }

  .command-item-title {
    font-weight: 600;
    font-size: 0.8rem;
  }

  .command-item-desc {
    font-size: 0.65rem;
    color: #6b7280;
    margin-top: 4px;
  }

  /* Message Actions */
  .message-actions {
    display: flex;
    gap: 6px;
    margin-top: 8px;
    opacity: 0;
    transition: opacity 0.2s;
  }

  .message:hover .message-actions { opacity: 1; }

  .msg-action-btn {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid var(--border-color);
    color: var(--primary-color);
    border-radius: 6px;
    padding: 4px 8px;
    cursor: pointer;
    font-size: 0.7rem;
    transition: all 0.2s;
  }

  .msg-action-btn:hover {
    background: rgba(34, 197, 94, 0.2);
    border-color: var(--primary-color);
  }

  /* Reactions */
  .reactions {
    display: flex;
    gap: 4px;
    margin-top: 6px;
    flex-wrap: wrap;
  }

  .reaction {
    background: rgba(22, 27, 34, 0.6);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .reaction:hover {
    background: rgba(34, 197, 94, 0.1);
    border-color: var(--primary-color);
  }

  .reaction.active {
    background: rgba(34, 197, 94, 0.15);
    border-color: var(--primary-color);
  }

  /* Skeleton Loaders */
  .skeleton {
    background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
  }

  @keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  .skeleton-line {
    height: 12px;
    border-radius: 4px;
    margin-bottom: 8px;
  }

  .skeleton-text {
    height: 40px;
    border-radius: 8px;
  }

  /* Voice Input */
  .voice-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    color: var(--primary-color);
    cursor: pointer;
    transition: all 0.2s;
    font-size: 1rem;
  }

  .voice-btn:hover {
    background: rgba(34, 197, 94, 0.2);
    border-color: var(--primary-color);
  }

  .voice-btn.recording {
    background: rgba(239, 68, 68, 0.2);
    border-color: #ef4444;
    color: #ef4444;
    animation: pulse-red 1.5s infinite;
  }

  @keyframes pulse-red {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  /* Confidence Badge */
  .confidence-badge {
    display: inline-block;
    background: rgba(34, 197, 94, 0.15);
    border: 1px solid rgba(34, 197, 94, 0.3);
    color: var(--primary-color);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    margin-left: 8px;
  }

  .confidence-badge.low {
    background: rgba(239, 68, 68, 0.15);
    border-color: rgba(239, 68, 68, 0.3);
    color: #fca5a5;
  }

  .confidence-badge.medium {
    background: rgba(251, 146, 60, 0.15);
    border-color: rgba(251, 146, 60, 0.3);
    color: #fdba74;
  }

  /* Related Questions */
  .related-questions {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.06);
  }

  .related-title {
    font-size: 0.7rem;
    color: #6b7280;
    margin-bottom: 8px;
    text-transform: uppercase;
  }

  .related-btn {
    display: block;
    width: 100%;
    background: rgba(34, 197, 94, 0.08);
    border: 1px solid rgba(34, 197, 94, 0.2);
    color: #9ca3af;
    padding: 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    cursor: pointer;
    text-align: left;
    margin-bottom: 6px;
    transition: all 0.2s;
    white-space: normal;
  }

  .related-btn:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    background: rgba(34, 197, 94, 0.12);
  }

  /* Floating Action Button */
  .fab-menu {
    position: fixed;
    bottom: 30px;
    right: 30px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: flex-end;
    z-index: 50;
  }

  .fab-item {
    width: 56px;
    height: 56px;
    background: linear-gradient(135deg, var(--primary-color), rgba(34, 197, 94, 0.8));
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #0a0a0a;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
    transition: all 0.2s;
    font-size: 1.2rem;
    border: none;
  }

  .fab-item:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4);
  }

  .fab-label {
    background: rgba(22, 27, 34, 0.9);
    color: var(--primary-color);
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 0.7rem;
    opacity: 0;
    pointer-events: none;
    transition: all 0.2s;
    white-space: nowrap;
    margin-right: 10px;
  }

  .fab-item:hover .fab-label {
    opacity: 1;
    pointer-events: auto;
  }

  /* Timestamp */
  .timestamp {
    font-size: 0.65rem;
    color: #4b5563;
    margin-top: 4px;
  }

  /* Main Container with Sidebar */
  .container {
    margin-left: 280px;
    display: flex;
    flex-direction: column;
    flex: 1;
    position: relative;
  }

  .container.full-width { margin-left: 0; }

  @media (max-width: 768px) {
    .sidebar { display: none; }
    .container { margin-left: 0; }
    .settings-panel { width: 280px; right: -280px; }
  }

  /* Header */
  header {
    background: rgba(22, 27, 34, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border-color);
    padding: 16px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 4px 30px rgba(0,0,0,0.3);
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .sidebar-toggle {
    background: none;
    border: none;
    color: var(--primary-color);
    cursor: pointer;
    font-size: 1.2rem;
    display: none;
  }

  @media (max-width: 768px) {
    .sidebar-toggle { display: block; }
  }

  .logo {
    width: 42px;
    height: 42px;
    background: linear-gradient(135deg, var(--primary-color), rgba(34, 197, 94, 0.8));
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
  }

  .header-title h1 {
    font-size: 1.2rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.3px;
  }
 
  .header-title p {
    font-size: 0.72rem;
    color: #6b7280;
    margin-top: 1px;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .header-btn {
    background: none;
    border: 1px solid var(--border-color);
    color: #9ca3af;
    border-radius: 8px;
    padding: 8px 12px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .header-btn:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    background: rgba(34, 197, 94, 0.05);
  }

  .status-badge {
    display: flex;
    align-items: center;
    gap: 7px;
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.75rem;
    color: var(--primary-color);
    font-weight: 500;
  }

  .status-dot {
    width: 7px;
    height: 7px;
    background: var(--primary-color);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
  }
 
  /* Main layout */
  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
    max-width: 900px;
    width: 100%;
    margin: 0 auto;
    padding: 24px 20px;
    position: relative;
    z-index: 1;
  }
 
  /* Welcome section */
  .welcome {
    text-align: center;
    padding: 40px 20px 30px;
  }
 
  .welcome-icon {
    font-size: 3.5rem;
    margin-bottom: 16px;
    display: block;
    filter: drop-shadow(0 0 20px rgba(34, 197, 94, 0.4));
  }
 
  .welcome h2 {
    font-size: 1.8rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 10px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
 
  .welcome p {
    color: #6b7280;
    font-size: 0.9rem;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.6;
  }
 
  /* Quick questions */
  .quick-questions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin: 20px 0;
  }
 
  .quick-btn {
    background: rgba(22, 27, 34, 0.8);
    border: 1px solid var(--border-color);
    color: #9ca3af;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 0.78rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: 'Inter', sans-serif;
  }
 
  .quick-btn:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    background: rgba(34, 197, 94, 0.08);
    transform: translateY(-1px);
  }
 
  /* Stats bar */
  .stats-bar {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin: 16px 0;
    flex-wrap: wrap;
  }
 
  .stat {
    background: rgba(22, 27, 34, 0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 8px 16px;
    text-align: center;
    font-size: 0.72rem;
  }
 
  .stat-value {
    color: var(--primary-color);
    font-weight: 700;
    font-size: 0.95rem;
    display: block;
  }
 
  .stat-label {
    color: #4b5563;
    margin-top: 2px;
  }
 
  /* Chat area */
  #chat-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 10px 0;
    min-height: 200px;
  }
 
  /* Messages */
  .message {
    display: flex;
    gap: 12px;
    animation: fadeIn 0.3s ease;
    position: relative;
  }
 
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
 
  .message.user { flex-direction: row-reverse; }
 
  .avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
  }
 
  .avatar.bot {
    background: linear-gradient(135deg, var(--primary-color), rgba(34, 197, 94, 0.8));
    box-shadow: 0 0 15px rgba(34, 197, 94, 0.3);
  }
 
  .avatar.user {
    background: linear-gradient(135deg, var(--secondary-color), rgba(59, 130, 246, 0.8));
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
  }
 
  .bubble {
    max-width: 75%;
    padding: 14px 18px;
    border-radius: 16px;
    line-height: 1.7;
    font-size: 0.9rem;
  }
 
  .bubble.bot {
    background: rgba(22, 27, 34, 0.9);
    border: 1px solid rgba(34, 197, 94, 0.15);
    border-bottom-left-radius: 4px;
    color: #e0e0e0;
  }
 
  .bubble.user {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(34, 197, 94, 0.08));
    border: 1px solid var(--border-color);
    border-bottom-right-radius: 4px;
    color: #e0e0e0;
  }
 
  .bubble.bot:hover, .bubble.user:hover {
    backdrop-filter: blur(10px);
  }

  .sources {
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 0.72rem;
    color: #4b5563;
    display: flex;
    align-items: center;
    gap: 5px;
    flex-wrap: wrap;
  }

  .source-badge {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.2);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 0.65rem;
    color: var(--primary-color);
    cursor: pointer;
    transition: all 0.2s;
  }

  .source-badge:hover {
    background: rgba(34, 197, 94, 0.15);
    border-color: var(--primary-color);
  }
 
  /* Typing indicator */
  .typing-bubble {
    background: rgba(22, 27, 34, 0.9);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    border-bottom-left-radius: 4px;
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 5px;
  }
 
  .typing-dot {
    width: 7px;
    height: 7px;
    background: var(--primary-color);
    border-radius: 50%;
    animation: bounce 1.2s infinite;
  }
 
  .typing-dot:nth-child(2) { animation-delay: 0.2s; }
  .typing-dot:nth-child(3) { animation-delay: 0.4s; }
 
  @keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-6px); opacity: 1; }
  }
 
  /* Input area */
  .input-wrapper {
    background: rgba(22, 27, 34, 0.95);
    backdrop-filter: blur(20px);
    border-top: 1px solid var(--border-color);
    padding: 20px;
    position: sticky;
    bottom: 0;
    z-index: 100;
  }
 
  .input-container {
    max-width: 900px;
    margin: 0 auto;
    display: flex;
    gap: 12px;
    align-items: flex-end;
  }
 
  .input-box {
    flex: 1;
    background: rgba(15, 17, 23, 0.8);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 14px 18px;
    color: #e0e0e0;
    font-size: 0.9rem;
    font-family: 'Inter', sans-serif;
    outline: none;
    resize: none;
    min-height: 52px;
    max-height: 140px;
    transition: border-color 0.2s;
    line-height: 1.5;
  }
 
  .input-box:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.08);
  }
 
  .input-box::placeholder { color: #374151; }
 
  .send-btn {
    width: 52px;
    height: 52px;
    background: linear-gradient(135deg, var(--primary-color), rgba(34, 197, 94, 0.8));
    border: none;
    border-radius: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
    flex-shrink: 0;
  }
 
  .send-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4); }
  .send-btn:active { transform: translateY(0); }
  .send-btn:disabled { background: #1f2937; box-shadow: none; cursor: not-allowed; transform: none; }
 
  .input-hint {
    text-align: center;
    font-size: 0.7rem;
    color: #374151;
    margin-top: 8px;
  }
 
  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 2px; }

  ::-webkit-scrollbar-thumb:hover { background: rgba(34, 197, 94, 0.4); }
 
  /* Mobile */
  @media (max-width: 600px) {
    header { padding: 12px 16px; }
    .main { padding: 16px 12px; }
    .welcome h2 { font-size: 1.4rem; }
    .bubble { max-width: 90%; }
    .stats-bar { gap: 8px; }
    .fab-menu { bottom: 20px; right: 20px; }
  }
</style>
</head>
<body>

<!-- Sidebar -->
<div class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <div class="sidebar-title">💬 Chat History</div>
    <button class="header-btn" onclick="toggleSidebar()" style="border: none; background: none;">✕</button>
  </div>
  <div id="history-list" style="flex: 1; overflow-y: auto;"></div>
  <button class="sidebar-btn" onclick="clearHistory()">🗑️ Clear History</button>
  <button class="sidebar-btn" onclick="exportChat()">📥 Export Chat</button>
</div>

<!-- Settings Panel -->
<div class="settings-panel" id="settings-panel">
  <div class="settings-header">
    <div class="settings-title">⚙️ Settings</div>
    <button class="close-settings" onclick="toggleSettings()">✕</button>
  </div>

  <div class="setting-group">
    <label class="setting-label">Theme</label>
    <div class="theme-picker">
      <button class="theme-option active" onclick="setTheme('dark')" title="Dark Mode">🌙 Dark</button>
      <button class="theme-option" onclick="setTheme('light')" title="Light Mode">☀️ Light</button>
    </div>
  </div>

  <div class="setting-group">
    <label class="setting-label">Accent Color</label>
    <div class="theme-picker">
      <button class="theme-option active" onclick="setColor('green')" style="background: rgba(34, 197, 94, 0.1); border-color: var(--primary-color);" title="Green">🟢 Green</button>
      <button class="theme-option" onclick="setColor('blue')" style="background: rgba(59, 130, 246, 0.1);" title="Blue">🔵 Blue</button>
    </div>
  </div>

  <div class="setting-group">
    <label class="setting-label">Response Tone</label>
    <select style="width: 100%; background: rgba(22, 27, 34, 0.8); border: 1px solid var(--border-color); border-radius: 6px; color: #fff; padding: 8px; cursor: pointer;">
      <option>Professional</option>
      <option>Casual</option>
      <option>Technical</option>
    </select>
  </div>

  <div class="setting-group">
    <label class="setting-label">Response Detail</label>
    <select style="width: 100%; background: rgba(22, 27, 34, 0.8); border: 1px solid var(--border-color); border-radius: 6px; color: #fff; padding: 8px; cursor: pointer;">
      <option>Concise</option>
      <option>Balanced</option>
      <option>Detailed</option>
    </select>
  </div>

  <div class="setting-group">
    <label class="setting-label">About</label>
    <p style="font-size: 0.75rem; color: #6b7280; line-height: 1.5;">
      Trading Chatbot v1.0<br>Powered by AI<br>© 2024 Your Company
    </p>
  </div>
</div>

<!-- Command Palette -->
<div class="command-palette" id="command-palette">
  <div class="command-input-wrapper">
    <input type="text" class="command-input" id="command-input" placeholder="Type a command... (e.g., /clear, /export, /history)" onkeydown="handleCommandKeydown(event)">
    <div class="command-list" id="command-list"></div>
  </div>
</div>

<!-- Main Container -->
<div class="container" id="container">
<header>
  <div class="header-left">
    <button class="sidebar-toggle" onclick="toggleSidebar()">☰</button>
    <div class="logo">📈</div>
    <div class="header-title">
      <h1>Trading Chatbot</h1>
      <p>Powered by your Trading Books • AI by Groq</p>
    </div>
  </div>
  <div class="header-actions">
    <button class="header-btn" onclick="openCommandPalette()" title="Commands">⌘</button>
    <button class="header-btn" onclick="toggleSettings()" title="Settings">⚙️</button>
    <div class="status-badge">
      <div class="status-dot"></div>
      Online
    </div>
  </div>
</header>
 
<div class="main">
  <div class="welcome" id="welcome-section">
    <span class="welcome-icon">📊</span>
    <h2>Your Personal Trading Assistant</h2>
    <p>Ask me anything about trading — from candlestick patterns to risk management strategies. Powered by expert trading books.</p>
 
    <div class="stats-bar">
      <div class="stat">
        <span class="stat-value">7</span>
        <span class="stat-label">Trading Books</span>
      </div>
      <div class="stat">
        <span class="stat-value">⚡ Fast</span>
        <span class="stat-label">AI Responses</span>
      </div>
      <div class="stat">
        <span class="stat-value">24/7</span>
        <span class="stat-label">Available</span>
      </div>
    </div>
 
    <div class="quick-questions">
      <button class="quick-btn" onclick="setQ('What is technical analysis?')">📊 Technical Analysis</button>
      <button class="quick-btn" onclick="setQ('Explain candlestick patterns')">🕯️ Candlestick Patterns</button>
      <button class="quick-btn" onclick="setQ('What is RSI indicator?')">📈 RSI Indicator</button>
      <button class="quick-btn" onclick="setQ('How to manage risk in trading?')">🛡️ Risk Management</button>
      <button class="quick-btn" onclick="setQ('What is support and resistance?')">📉 Support & Resistance</button>
      <button class="quick-btn" onclick="setQ('Explain MACD indicator')">⚡ MACD</button>
      <button class="quick-btn" onclick="setQ('What is a bullish engulfing pattern?')">🕯️ Bullish Engulfing</button>
      <button class="quick-btn" onclick="setQ('How to start trading as a beginner?')">🚀 Beginner Guide</button>
      <button class="quick-btn" onclick="setQ('What is moving average?')">〰️ Moving Average</button>
      <button class="quick-btn" onclick="setQ('Explain moving average crossover strategy')">📉 MA Crossover</button>
    </div>
  </div>
 
  <div id="chat-box"></div>
</div>
 
<div class="input-wrapper">
  <div class="input-container">
    <button class="voice-btn" id="voice-btn" onclick="toggleVoiceInput()" title="Voice Input">🎤</button>
    <textarea
      id="user-input"
      class="input-box"
      placeholder="Ask anything about trading..."
      rows="1"
      onkeydown="handleKey(event)"
      oninput="autoResize(this)"
    ></textarea>
    <button class="send-btn" id="send-btn" onclick="sendMsg()">➤</button>
  </div>
  <div class="input-hint">Press Enter to send • Shift+Enter for new line • ⌘ for commands</div>
</div>

<!-- Floating Action Buttons -->
<div class="fab-menu">
  <button class="fab-item" onclick="exportChat()" title="Export">
    <span class="fab-label">Export</span>
    📥
  </button>
  <button class="fab-item" onclick="clearHistory()" title="Clear">
    <span class="fab-label">Clear</span>
    🗑️
  </button>
</div>

</div>

<script>
let chatHistory = [];
let isRecording = false;
let recognition = null;
let conversationCount = 0;

// Basic functions
function setQ(text) {
  document.getElementById('user-input').value = text;
  document.getElementById('user-input').focus();
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMsg();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 140) + 'px';
}

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('collapsed');
}

function toggleSettings() {
  const settingsPanel = document.getElementById('settings-panel');
  settingsPanel.classList.toggle('open');
}

function openCommandPalette() {
  const palette = document.getElementById('command-palette');
  palette.classList.add('open');
  document.getElementById('command-input').focus();
}

function closeCommandPalette() {
  const palette = document.getElementById('command-palette');
  palette.classList.remove('open');
}

function setTheme(theme) {
  document.body.classList.remove('light-mode');
  if (theme === 'light') {
    document.body.classList.add('light-mode');
  }
  localStorage.setItem('theme', theme);
}

function setColor(color) {
  localStorage.setItem('color', color);
}

function clearHistory() {
  if (confirm('Clear all chat history?')) {
    chatHistory = [];
    localStorage.removeItem('chatHistory');
    document.getElementById('chat-box').innerHTML = '';
    document.getElementById('welcome-section').style.display = 'block';
  }
}

function exportChat() {
  const messages = document.querySelectorAll('.message');
  let content = 'Trading Chatbot Export\n';
  messages.forEach(msg => {
    const isUser = msg.classList.contains('user');
    const bubble = msg.querySelector('.bubble');
    content += (isUser ? 'You' : 'Bot') + ':\n' + bubble.textContent + '\n\n';
  });
  
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'chat.txt';
  a.click();
}

function toggleVoiceInput() {
  alert('Voice input coming soon');
}

function copyMessage(btn) {
  const message = btn.closest('.message-actions').parentElement.querySelector('.bubble').textContent;
  navigator.clipboard.writeText(message).then(() => {
    btn.textContent = '✓ Copied';
    setTimeout(() => btn.textContent = '📋 Copy', 2000);
  });
}

function addReaction(btn, emoji) {
  alert('Reactions coming soon');
}

function addMessage(text, isUser, sources) {
  const chatBox = document.getElementById('chat-box');
  const msg = document.createElement('div');
  msg.className = 'message ' + (isUser ? 'user' : 'bot');
  
  const avatar = document.createElement('div');
  avatar.className = 'avatar ' + (isUser ? 'user' : 'bot');
  avatar.textContent = isUser ? '👤' : '📈';
  
  const contentWrapper = document.createElement('div');
  contentWrapper.style.flex = '1';
  
  const bubble = document.createElement('div');
  bubble.className = 'bubble ' + (isUser ? 'user' : 'bot');
  bubble.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');
  
  contentWrapper.appendChild(bubble);
  
  if (!isUser && sources && sources.length > 0) {
    const srcDiv = document.createElement('div');
    srcDiv.className = 'sources';
    srcDiv.innerHTML = sources.map(s => '<span class="source-badge">' + escapeHtml(s) + '</span>').join('');
    contentWrapper.appendChild(srcDiv);
  }
  
  const timestamp = document.createElement('div');
  timestamp.className = 'timestamp';
  timestamp.textContent = new Date().toLocaleTimeString();
  contentWrapper.appendChild(timestamp);
  
  msg.appendChild(avatar);
  msg.appendChild(contentWrapper);
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showTyping() {
  const chatBox = document.getElementById('chat-box');
  const msg = document.createElement('div');
  msg.className = 'message bot';
  msg.id = 'typing-indicator';
  
  const avatar = document.createElement('div');
  avatar.className = 'avatar bot';
  avatar.textContent = '📈';
  
  const bubble = document.createElement('div');
  bubble.className = 'typing-bubble';
  bubble.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
  
  msg.appendChild(avatar);
  msg.appendChild(bubble);
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTyping() {
  const t = document.getElementById('typing-indicator');
  if (t) t.remove();
}

async function sendMsg() {
  const input = document.getElementById('user-input');
  const question = input.value.trim();
  if (!question) return;
  
  document.getElementById('welcome-section').style.display = 'none';
  
  addMessage(question, true, []);
  input.value = '';
  input.style.height = 'auto';
  
  const btn = document.getElementById('send-btn');
  btn.disabled = true;
  showTyping();
  
  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: question })
    });
    const data = await response.json();
    hideTyping();
    addMessage(data.answer, false, data.sources);
  } catch (err) {
    hideTyping();
    addMessage('Error: ' + err.message, false, []);
  }
  
  btn.disabled = false;
  input.focus();
}

function escapeHtml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  const savedTheme = localStorage.getItem('theme') || 'dark';
  setTheme(savedTheme);
  
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeCommandPalette();
    }
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      openCommandPalette();
    }
  });
});
</script>
</body>
</html>
"""
 
@app.route("/")
def index():
    return render_template_string(HTML_PAGE)
 
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"answer": "Please ask a question.", "sources": []})
 
    try:
        result = qa_chain({"query": question})
        answer = result["result"]
        sources = list(set(
            doc.metadata.get("source", "")
            for doc in result.get("source_documents", [])
            if doc.metadata.get("source")
        ))
        return jsonify({"answer": answer, "sources": sources})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}", "sources": []})
 
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"\n✅ Trading Chatbot running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)