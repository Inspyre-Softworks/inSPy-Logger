"""
Author: Taylor B. tayjaybabee@gmail.com
Date: 2024-11-23 13:09:11
LastEditors: Taylor B. tayjaybabee@gmail.com
LastEditTime: 2024-11-27 20:23:35
FilePath: inspy_logger/engine/adapters/thread.py
Description: 这是默认设置,可以在设置》工具》File Description中进行配置
"""
import logging
import threading


class ThreadAdapter(logging.LoggerAdapter):
    """
    A class that adapts a logger to work with threads.
    """
    def process(self, msg, kwargs):
        """
        Processes the message and keyword arguments.

        Parameters:
            msg (str): The message to log.
            kwargs (Dict): The keyword arguments to log.

        Returns:
            Tuple: A tuple containing the message and keyword arguments.
        """
        # Add context to the log message.
        thread_name = threading.current_thread().name

        if thread_name != 'MainThread':
            msg = f'[Thread - {thread_name}] {msg}'

        return msg, kwargs
