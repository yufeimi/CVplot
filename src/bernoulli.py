import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yaml
from meta_data import CVMetaData

from smooth import *

# Global variables
S = 1.397  # Cross section area (height in 2D)
c = 34000  # Sound speed
rho = 1.3e-3  # Air density
mu = 1.8e-4  # Air viscosity
to_newton = 1e-5  # Convert from dyne to Newton
to_pa = 1e-1  # Convert from dyne/cm^2 to Pascal
to_watt = 1e-7  # Convert from erg/s to Watt
to_m2s2 = 1e-4  # Convert from cm^2/s^2 to m^2/s^2


def create_bernoulli_frame(cv_data):
    atm = 1013250.0
    # Copy energy columns
    cv_bernoulli = cv_data[["Time", "Normalized time"]].copy()
    # Contraction region
    cv_bernoulli["Econ contraction"] = cv_data["Rate convection contraction"].to_numpy(
        copy=True) / 4
    cv_bernoulli["Epre contraction"] = cv_data["Rate pressure contraction"].to_numpy(
        copy=True) / 4
    cv_bernoulli["Eden contraction"] = cv_data["Rate density contraction"].to_numpy(
        copy=True) / 4
    cv_bernoulli["Evis contraction"] = -cv_data["Rate friction contraction"].to_numpy(
        copy=True) / 4
    cv_bernoulli["Euns contraction"] = cv_data["Acceleration contraction"].to_numpy(
        copy=True) / 4

    cv_bernoulli["Residual contraction"] = cv_bernoulli["Econ contraction"] + \
        cv_bernoulli["Epre contraction"] + cv_bernoulli["Euns contraction"] + \
        cv_bernoulli["Evis contraction"] + cv_bernoulli["Eden contraction"]

    # Jet region
    cv_bernoulli["Econ jet"] = cv_data["Rate convection jet"].to_numpy(
        copy=True) / 4
    cv_bernoulli["Epre jet"] = cv_data["Rate pressure jet"].to_numpy(
        copy=True) / 4
    cv_bernoulli["Eden jet"] = cv_data["Rate density jet"].to_numpy(
        copy=True) / 4
    cv_bernoulli["Evis jet"] = -cv_data["Rate friction jet"].to_numpy(
        copy=True) / 4
    cv_bernoulli["Euns jet"] = cv_data["Acceleration jet"].to_numpy(
        copy=True) / 4

    cv_bernoulli["Residual jet"] = cv_bernoulli["Econ jet"] + \
        cv_bernoulli["Epre jet"] + cv_bernoulli["Euns jet"] + \
        cv_bernoulli["Evis jet"] + cv_bernoulli["Eden jet"]

    print(cv_bernoulli)
    # Combined
    cv_bernoulli["Econ combined"] = cv_bernoulli["Econ contraction"].to_numpy(
        copy=True) + cv_bernoulli["Econ jet"].to_numpy(copy=True)
    cv_bernoulli["Epre combined"] = cv_bernoulli["Epre contraction"].to_numpy(
        copy=True) + cv_bernoulli["Epre jet"].to_numpy(copy=True)
    cv_bernoulli["Eden combined"] = cv_bernoulli["Eden jet"].to_numpy(
        copy=True) + cv_bernoulli["Eden contraction"].to_numpy(copy=True)
    cv_bernoulli["Evis combined"] = cv_bernoulli["Evis jet"].to_numpy(
        copy=True) + cv_bernoulli["Evis contraction"].to_numpy(copy=True)
    cv_bernoulli["Euns combined"] = cv_bernoulli["Euns jet"].to_numpy(
        copy=True) + cv_bernoulli["Euns contraction"].to_numpy(copy=True)
    cv_bernoulli["Residual combined"] = cv_bernoulli["Residual contraction"] + \
        cv_bernoulli["Residual jet"]

    # Trace for the endpoints
    cv_bernoulli["Contraction endpoint"] = cv_data[" Contraction end xcoord"].to_numpy(
        copy=True)/100/to_m2s2
    cv_bernoulli["Jet endpoint"] = cv_data[" Jet start xcoord"].to_numpy(
        copy=True)/100/to_m2s2

    # Convert the unit
    for label, content in cv_bernoulli.items():
        if label != "Time" and label != "Normalized time":
            cv_bernoulli[label] = content * to_m2s2

    return cv_bernoulli


def main():
    meta_data = CVMetaData(sys.argv)
    documents = meta_data.documents
    # Read CV data file
    cv_data = pd.read_csv(meta_data.filename, header=0)

    # Time
    time = cv_data["Time"]
    # Time span
    normalized_timespan = [0, meta_data.n_period]
    time_to_plot = meta_data.timespan[1] - meta_data.timespan[0]
    T_cycle = time_to_plot/meta_data.n_period
    cv_data["Normalized time"] = (
        cv_data["Time"] - meta_data.timespan[0])/T_cycle

    cv_bernoulli = create_bernoulli_frame(cv_data)

    # smooth
    smooth_range = 100
    smooth_data(cv_bernoulli, meta_data, smooth_range)

    # Figure properties
    height = meta_data.size["height"]
    width = meta_data.size["width"]
    label_size = 36
    plt.rcParams["figure.figsize"] = [width, height]
    plt.rcParams["xtick.labelsize"] = label_size
    plt.rcParams["ytick.labelsize"] = label_size


plt.rcParams["figure.subplot.left"] = meta_data.size["left"]
plt.rcParams["figure.subplot.right"] = meta_data.size["right"]

   def apply_fig_settings(fig):
        axis_label_size = 36
        plt.locator_params(axis='y', nbins=8)
        fig.tick_params(direction='in', length=20,
                        width=2, top=True, right=True)
        fig.get_legend().remove()
        fig.grid()
        fig.set_xlim(normalized_timespan)
        fig.set_xlabel("t/T", fontsize=axis_label_size)
        fig.set_ylabel("Bernoulli Equation Terms ($m^2/s^2$)",
                       fontsize=axis_label_size)

    def draw_open_close(fig):
        # open_glottis = [0.078, 0.895]
        fig.set_ylim(fig.get_ylim())
        plt.plot([meta_data.open_glottis[0], meta_data.open_glottis[0]],
                 fig.get_ylim(), 'r--', linewidth=4)
        plt.plot([meta_data.open_glottis[1], meta_data.open_glottis[1]],
                 fig.get_ylim(), 'r--', linewidth=4)

    fig_8a = cv_bernoulli.plot(x="Normalized time",
                               y=["Contraction endpoint", "Jet endpoint"],
                               style=['-', '-.'],
                               color=['b', 'lightgreen'], lw=5)
    apply_fig_settings(fig_8a)
    fig_8a.set_ylabel("X position (m)")
    plt.plot(fig_8a.get_xlim(),
             [0.125, 0.125], 'k', linewidth=5)
    plt.plot(fig_8a.get_xlim(),
             [0.15, 0.15], 'm', linewidth=5)
    plt.ylim([0.122, 0.153])
    draw_open_close(fig_8a)
    # plt.tight_layout()
    plt.savefig(meta_data.output_dir + "/8a.png", format='png')

    fig_9a = cv_bernoulli.plot(
        x="Normalized time",
        y=["Econ combined", "Epre combined", "Euns combined",
            "Eden combined", "Evis combined"],
        style=['-', '-', '--', '-.', '--'],
        color=['b', 'r', 'k', 'm', 'lightgreen'], markevery=20, lw=5)
    apply_fig_settings(fig_9a)
    draw_open_close(fig_9a)
    # plt.tight_layout()
    plt.savefig(meta_data.output_dir + "/9a.png", format='png')

    fig_9b = cv_bernoulli.plot(
        x="Normalized time",
        y=["Econ contraction", "Epre contraction", "Euns contraction",
            "Eden contraction", "Evis contraction"],
        style=['-', '-', '--', '-.', '--'],
        color=['b', 'r', 'k', 'm', 'lightgreen'], markevery=20, lw=5)
    apply_fig_settings(fig_9b)
    draw_open_close(fig_9b)
    # plt.tight_layout()
    plt.savefig(meta_data.output_dir + "/9b.png", format='png')

    fig_9c = cv_bernoulli.plot(
        x="Normalized time",
        y=["Econ jet", "Epre jet", "Euns jet",
            "Eden jet", "Evis jet"],
        style=['-', '-', '--', '-.', '--'],
        color=['b', 'r', 'k', 'm', 'lightgreen'], markevery=20, lw=5)
    apply_fig_settings(fig_9c)
    draw_open_close(fig_9c)
    # plt.tight_layout()
    plt.savefig(meta_data.output_dir + "/9c.png", format='png')
    plt.show()


if __name__ == "__main__":
    main()
