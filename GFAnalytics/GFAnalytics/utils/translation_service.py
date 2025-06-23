#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Translation Service Module

This module provides translation services for plot labels and feature names.
It handles the conversion of English labels to Chinese for visualization purposes.
"""

import logging

logger = logging.getLogger('GFAnalytics.TranslationService')

class TranslationService:
    """
    Handles translation of plot labels and feature names to Chinese.
    """
    
    @staticmethod
    def translate_feature_name(feature_name):
        """
        Translate a feature name to Chinese.
        
        Args:
            feature_name (str): The feature name to translate.
            
        Returns:
            str: The translated feature name.
        """
        # Remove 'cs_' prefix if present
        if feature_name.startswith('cs_'):
            feature_name = feature_name[3:]
            
        # Split the feature name into components
        components = feature_name.split('_')
        
        # Translate each component
        translated_components = []
        for component in components:
            if component == 'base':
                translated_components.append('本')
            elif component == 'current':
                translated_components.append('流')
            elif component == 'minus':
                translated_components.append('负')
            elif component == 'year':
                translated_components.append('年')
            elif component == 'month':
                translated_components.append('月')
            elif component == 'day':
                translated_components.append('日')
            elif component == 'hour':
                translated_components.append('时')
            else:
                translated_components.append(component)
        
        # Join the components
        return ''.join(translated_components)
    
    @staticmethod
    def translate_plot_labels():
        """
        Get translations for common plot labels.
        
        Returns:
            dict: Dictionary of plot label translations.
        """
        return {
            # General plot labels
            'Date': '日期',
            'Price': '价格',
            'Importance': '重要性',
            'Feature': '特征',
            'Average Prediction': '平均预测值',
            'Prediction': '预测值',
            'Historical Close Price': '历史收盘价',
            'Predicted Price': '预测价格',
            'Confidence Interval': '置信区间',
            
            # Plot titles
            'Feature Importance (Top 30 Features)': '特征重要性 (前30个特征)',
            'Feature Correlation Heatmap': '特征相关性热图',
            'Average Prediction by': '按以下特征的平均预测值',
            
            # Bazi specific labels
            'Year Pillar': '年柱',
            'Month Pillar': '月柱',
            'Day Pillar': '日柱',
            'Hour Pillar': '时柱',
            
            # Evaluation metrics
            'MSE': '均方误差',
            'RMSE': '均方根误差',
            'R2': '决定系数',
            'MedAE': '中位数绝对误差',
            'MAE': '平均绝对误差',
            'EVS': '解释方差分数'
        }
    
    @staticmethod
    def translate_feature_names(feature_names):
        """
        Translate a list of feature names to Chinese.
        
        Args:
            feature_names (list): List of feature names to translate.
            
        Returns:
            list: List of translated feature names.
        """
        return [TranslationService.translate_feature_name(name) for name in feature_names] 