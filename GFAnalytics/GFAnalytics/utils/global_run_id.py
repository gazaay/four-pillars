#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Run ID Module

This module provides a global run ID for the GFAnalytics framework.
The run ID is generated once per execution and can be accessed by any component.
"""

import uuid
import datetime
import logging

logger = logging.getLogger('GFAnalytics.GlobalRunID')

# The global run ID variable
_run_id = None

def generate_run_id():
    """
    Generate a unique run ID for the current execution.
    The run ID is a combination of timestamp and UUID.
    
    Returns:
        str: Unique run ID
    """
    global _run_id
    if _run_id is None:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        _run_id = f"{timestamp}_{unique_id}"
        logger.info(f"Generated new run ID: {_run_id}")
    return _run_id

def get_run_id():
    """
    Get the current run ID. If not already generated, creates a new one.
    
    Returns:
        str: Current run ID
    """
    global _run_id
    if _run_id is None:
        return generate_run_id()
    return _run_id

def reset_run_id():
    """
    Reset the run ID to None, forcing a new generation on next call.
    Useful for testing or when explicitly starting a new execution.
    """
    global _run_id
    _run_id = None
    logger.info("Run ID reset to None") 