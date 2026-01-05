#!/usr/bin/env python3
"""
Script para ejecutar el chat interactivo de trading BTC/USDT
"""
import sys
import os

# Add src to path
sys.path.append('src')

from chat.chat_interface import ChatInterface


if __name__ == "__main__":
    chat = ChatInterface()
    chat.run()
