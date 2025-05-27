#!/bin/bash

mkdir -p logs

echo "Starting NileEdge Email Agent in scheduled mode..."
nohup python app/email_agent.py --mode scheduled --interval 300 > logs/email_agent.out.log 2> logs/email_agent.err.log &

echo "Starting NileEdge AI Chatbot server..."
nohup python server.py > logs/server.out.log 2> logs/server.err.log &
