import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from sklearn.metrics import r2_score, root_mean_squared_error
from matplotlib.cm import ScalarMappable
from scipy import stats
import sys
import os

sys.path.append(os.path.abspath(".."))
from data_tools import my_setup

class PlotPlantower:

    def __init__(self):
        self.vmin = 0
        self.vmax = 60
        self.temp_norm = Normalize(vmin=self.vmin, vmax=self.vmax)

    def plot(self, data, sensor_id,period):
        # Set up 2x2 grid of subplots
        fig, axs = plt.subplots(2, 2, figsize=(14,12))
        fig.suptitle(f"{period} Data: {sensor_id} Calibration Model Comparison\n", fontsize=18)
        fig.text(0.5, 0.92, "Unit-Specific Models", ha='center', fontsize=14, fontweight='bold')
        fig.subplots_adjust(hspace=0.3)  # increase vertical space between rows
        fig.text(0.5,0.48,"Universal Models", ha='center', fontsize=14, fontweight='bold' )

        self._add_to_plots(0,0,'pm_calibrated_clarityremake', 'Clarity v2 Variables - PM10', axs, data)
        self._add_to_plots(0,1,'pm_calibrated_twovar', 'RH + PM2.5', axs, data)
        self._add_to_plots(1,1,'pm_calibrated_epa_barkjohn', 'EPA Barkjohn 2021', axs, data)
        self._add_to_plots(1,0,'pm_calibrated_clarity', 'Clarity v2', axs, data)
        imagefolder = my_setup.local_image_folder("Plantower")
        plt.savefig(rf"{imagefolder}{sensor_id}/{period}CalibrationStatswEPA.jpg", format='jpg', dpi=300)

        fig, ax = plt.subplots(figsize=(7,6))
        self._add_to_plots(0,0,'m_PM25_CF1', 'Raw Plantower CF1', ax, data)  # pass ax instead of axs grid
        plt.savefig(rf"{imagefolder}{sensor_id}/RawStats.jpg", format='jpg', dpi=300)


    def _add_to_plots(self, i, j, model, name, axs, data):
    # If axs is a 2D array (grid)
        if isinstance(axs, np.ndarray):
            ax = axs[i, j]
        else:
            ax = axs  # single subplot case

        x = data['reference']
        y = data[model]

        ax.scatter(
            x,
            y,
            c=data['temp_C'],
            cmap='RdBu_r',
            norm=self.temp_norm,
            alpha=0.8,
            s=5
        )

        # Add 1:1 line
        ax.plot([0, 100], [0, 100], c='black', linestyle='--', label='1:1')

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        y_fit = slope * x + intercept

        ax.plot(x, y_fit, c = 'red', label = 'Best fit')

        # Metrics
        r2, rmse, mbe, nmb, nme = self._calculate_metrics(data['reference'], data[model])
        ax.text(0.1, 0.95, f'R\u00b2 = {r2:.2f}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.1, 0.87, f'RMSE = {rmse:.2f}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.1, 0.80, f'MBE = {mbe:.2f}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.1, 0.73, f'NMB = {nmb:.2%}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.1, 0.66, f'NME = {nme:.2%}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.1, 0.59, f'Data Points = {len(data)}', transform=ax.transAxes, fontsize=13, verticalalignment='top')
        ax.text(0.55, 0.03, f'y = {slope:.2f}x + {intercept:.2f}',transform=ax.transAxes, fontsize=13, verticalalignment='bottom')

        # Colorbar
        sm = ScalarMappable(cmap='RdBu_r', norm=self.temp_norm)
        sm.set_array([])
        ticks = np.arange(self.vmin, self.vmax + 1, 5)
        cbar = plt.colorbar(sm, ax=ax, ticks=ticks)
        cbar.set_ticklabels([str(t) for t in ticks])
        cbar.set_label('Ambient Temp [C]', fontsize=12)

        # Titles & labels
        ax.set_title(f'{name}', fontsize=14)
        ax.set_xlabel('Reference PM (ug/m3)', fontsize=14)
        ax.set_ylabel(f'Calibrated PM (ug/m3)', fontsize=14)

        ax.set_xlim(0, 65)
        ax.set_ylim(0, 65)

    # Function to calculate metrics
    def _calculate_metrics(self, observed, predicted):
        r2 = r2_score(observed, predicted)
        rmse = root_mean_squared_error(observed, predicted)
        mbe = (predicted - observed).mean()
        
        # Calculate percentage errors, handling division by zero
        nmb = np.nanmean(np.divide(predicted - observed, observed, out=np.zeros_like(predicted - observed), where=observed!=0))
        nme = np.nanmean(np.divide(abs(predicted - observed), observed, out=np.zeros_like(abs(predicted - observed)), where=observed!=0))
        
        return r2, rmse, mbe, nmb, nme

class PlotSensirion:
    def __init__(self):
        self.vmin = 0
        self.vmax = 60
        self.temp_norm = Normalize(vmin=self.vmin, vmax=self.vmax)

    def plot(self, data, sensor_id,period):
        # Set up 1x3 grid of subplots
        fig, axs = plt.subplots(1, 3, figsize=(18,6))
        fig.suptitle(f"{period} Data: {sensor_id} Calibration Model Comparison\n", fontsize=16)
        fig.subplots_adjust(hspace=0.3)  # increase vertical space between rows
        self._add_to_plots(2,'pm_calibrated_clarityremake', 'Clarity v2 Variables - PM10', axs, data)
        self._add_to_plots(1,'pm_calibrated_twovar', 'RH + PM2.5', axs, data)
        self._add_to_plots(0,'m_PM25_b', 'Raw Data', axs, data)
        imagefolder = my_setup.local_image_folder("Sensirion")
        plt.savefig(rf"{imagefolder}{sensor_id}/{period}CalibrationStats.jpg", format='jpg', dpi=300)

    def _add_to_plots(self, i, model, name, axs, data):
    # If axs is a 2D array (grid)
        if isinstance(axs, np.ndarray):
            ax = axs[i]
        else:
            ax = axs  # single subplot case

        x = data['reference']
        y = data[model]

        ax.scatter(
            x,
            y,
            c=data['temp_C'],
            cmap='RdBu_r',
            norm=self.temp_norm,
            alpha=0.8,
            s=5
        )

        # Add 1:1 line
        ax.plot([0, 100], [0, 100], c='black', linestyle='--', label='1:1')

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        y_fit = slope * x + intercept

        ax.plot(x, y_fit, c = 'red', label = 'Best fit')

        # Metrics
        r2, rmse, mbe, nmb, nme = self._calculate_metrics(data['reference'], data[model])
        ax.text(0.1, 0.95, f'R\u00b2 = {r2:.2f}', transform=ax.transAxes, fontsize=11, verticalalignment='top')
        ax.text(0.1, 0.87, f'RMSE = {rmse:.2f}', transform=ax.transAxes, fontsize=11, verticalalignment='top')
        ax.text(0.1, 0.80, f'MBE = {mbe:.2f}', transform=ax.transAxes, fontsize=11, verticalalignment='top')
        ax.text(0.1, 0.73, f'NMB = {nmb:.2%}', transform=ax.transAxes, fontsize=11, verticalalignment='top')
        ax.text(0.1, 0.66, f'NME = {nme:.2%}', transform=ax.transAxes, fontsize=11, verticalalignment='top')
        ax.text(0.1, 0.59, f'Data Points = {len(data)}', transform=ax.transAxes, fontsize=11, verticalalignment='top')
        ax.text(0.55, 0.03, f'y = {slope:.2f}x + {intercept:.2f}',transform=ax.transAxes, fontsize=11, verticalalignment='bottom')

        # Colorbar
        sm = ScalarMappable(cmap='RdBu_r', norm=self.temp_norm)
        sm.set_array([])
        ticks = np.arange(self.vmin, self.vmax + 1, 5)
        cbar = plt.colorbar(sm, ax=ax, ticks=ticks)
        cbar.set_ticklabels([str(t) for t in ticks])
        cbar.set_label('Ambient Temp [C]', fontsize=12)

        # Titles & labels
        ax.set_title(f'{name}', fontsize=14)
        ax.set_xlabel('Reference PM (ug/m3)', fontsize=14)
        ax.set_ylabel(f'Calibrated PM (ug/m3)', fontsize=14)

        ax.set_xlim(0, 80)
        ax.set_ylim(0, 80)

    # Function to calculate metrics
    def _calculate_metrics(self, observed, predicted):
        r2 = r2_score(observed, predicted)
        rmse = root_mean_squared_error(observed, predicted)
        mbe = (predicted - observed).mean()
        
        # Calculate percentage errors, handling division by zero
        nmb = np.nanmean(np.divide(predicted - observed, observed, out=np.zeros_like(predicted - observed), where=observed!=0))
        nme = np.nanmean(np.divide(abs(predicted - observed), observed, out=np.zeros_like(abs(predicted - observed)), where=observed!=0))
        
        return r2, rmse, mbe, nmb, nme
