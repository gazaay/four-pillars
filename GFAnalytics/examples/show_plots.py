#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example script demonstrating how to run the GFAnalytics framework and display plots.
"""

import os
import sys
import matplotlib.pyplot as plt

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GFAnalytics.main import GFAnalytics

def main():
    """Example of running GFAnalytics with plot display."""
    print("Running GFAnalytics with plot display...")
    
    # Create an instance of the GFAnalytics framework
    gf = GFAnalytics()
    
    # Option 1: Run the complete pipeline with plot display during execution
    print("\nOption 1: Run complete pipeline with plot display during execution...")
    # This will show plots as they are created
    results = gf.run(show_plots=True)
    
    # Option 2: Run the pipeline without showing plots, then display later
    print("\nOption 2: Run pipeline without showing plots, then display later...")
    gf = GFAnalytics()  # Create a new instance
    results = gf.run(show_plots=False)  # Don't show plots during execution
    
    # Now display all plots at once
    print("Displaying all plots...")
    gf.display_plots()
    
    # Option 3: Display specific plots only
    print("\nOption 3: Display specific plots only...")
    # Create a prediction plot and display it
    gf.plotter.plot_prediction(gf.stock_data, gf.predictions, show=True)
    
    # Create a feature importance plot and display it
    gf.plotter.plot_feature_importance(gf.model, gf.training_data, show=True)
    
    # Option 4: Use matplotlib directly
    print("\nOption 4: Use matplotlib directly...")
    # Create plots without showing them
    prediction_fig = gf.plotter.plot_prediction(gf.stock_data, gf.predictions, show=False)
    feature_fig = gf.plotter.plot_feature_importance(gf.model, gf.training_data, show=False)
    
    # Now show them using matplotlib
    plt.figure(prediction_fig.number)
    plt.figure(feature_fig.number)
    plt.show()
    
    print("\nPlot display demonstration complete.")
    return results

if __name__ == "__main__":
    main() 