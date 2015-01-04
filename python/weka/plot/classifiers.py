# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# classifiers.py
# Copyright (C) 2014 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
import weka.plot as plot
if plot.matplotlib_available:
    import matplotlib.pyplot as plt
from weka.core.classes import JavaObject
from weka.core.dataset import Instances
from weka.classifiers import NumericPrediction, NominalPrediction

# logging setup
logger = logging.getLogger(__name__)


def plot_classifier_errors(predictions, absolute=True, max_relative_size=50, absolute_size=50, title=None,
                           outfile=None, wait=True):
    """
    Plots the classifers for the given list of predictions.
    TODO: click events http://matplotlib.org/examples/event_handling/data_browser.html
    :param predictions: the predictions to plot
    :type predictions: list
    :param absolute: whether to use absolute errors as size or relative ones
    :type absolute: bool
    :param max_relative_size: the maximum size in point in case of relative mode
    :type max_relative_size: int
    :param absolute_size: the size in point in case of absolute mode
    :type absolute_size: int
    :param title: an optional title
    :type title: str
    :param outfile: the output file, ignored if None
    :type outfile: str
    :param wait: whether to wait for the user to close the plot
    :type wait: bool
    """
    if not plot.matplotlib_available:
        logger.error("Matplotlib is not installed, plotting unavailable!")
        return
    actual = []
    predicted = []
    error = None
    cls = None
    for pred in predictions:
        actual.append(pred.actual)
        predicted.append(pred.predicted)
        if isinstance(pred, NumericPrediction):
            if error is None:
                error = []
            error.append(abs(pred.error))
        elif isinstance(pred, NominalPrediction):
            if cls is None:
                cls = []
            if pred.actual != pred.predicted:
                cls.append(1)
            else:
                cls.append(0)
    fig, ax = plt.subplots()
    if error is None and cls is None:
        ax.scatter(actual, predicted, s=absolute_size, alpha=0.5)
    elif not cls is None:
        ax.scatter(actual, predicted, c=cls, s=absolute_size, alpha=0.5)
    elif not error is None:
        if not absolute:
            min_err = min(error)
            max_err = max(error)
            factor = (max_err - min_err) / max_relative_size
            for i in xrange(len(error)):
                error[i] = error[i] / factor * max_relative_size
        ax.scatter(actual, predicted, s=error, alpha=0.5)
    ax.set_xlabel("actual")
    ax.set_ylabel("predicted")
    if title is None:
        title = "Classifier errors"
    ax.set_title(title)
    ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", c="0.3")
    ax.grid(True)
    fig.canvas.set_window_title(title)
    plt.draw()
    if not outfile is None:
        plt.savefig(outfile)
    if wait:
        plt.show()


def generate_thresholdcurve_data(evaluation, class_index):
    """
    Generates the threshold curve data from the evaluation object's predictions.
    :param evaluation: the evaluation to obtain the predictions from
    :type evaluation: Evaluation
    :param class_index: the 0-based index of the class-label to create the plot for
    :type class_index: int
    :return: the generated threshold curve data
    :rtype: Instances
    """
    jtc = JavaObject.new_instance("weka.classifiers.evaluation.ThresholdCurve")
    pred = javabridge.call(evaluation.jobject, "predictions", "()Ljava/util/ArrayList;")
    result = Instances(
        javabridge.call(jtc, "getCurve", "(Ljava/util/ArrayList;I)Lweka/core/Instances;", pred, class_index))
    return result


def get_thresholdcurve_data(data, xname, yname):
    """
    Retrieves x and y columns from  of the data generated by the weka.classifiers.evaluation.ThresholdCurve
    class.
    :param data: the threshold curve data
    :type data: Instances
    :param xname: the name of the X column
    :type xname: str
    :param yname: the name of the Y column
    :type yname: str
    :return: tuple of x and y arrays
    :rtype: tuple
    """
    xi = data.attribute_by_name(xname).index
    yi = data.attribute_by_name(yname).index
    x = []
    y = []
    for i in xrange(data.num_instances):
        inst = data.get_instance(i)
        x.append(inst.get_value(xi))
        y.append(inst.get_value(yi))
    return x, y


def get_auc(data):
    """
    Calculates the area under the ROC curve (AUC).
    :param data: the threshold curve data
    :type data: Instances
    :return: the area
    :rtype: float
    """
    return javabridge.static_call(
        "weka/classifiers/evaluation/ThresholdCurve", "getROCArea", "(Lweka/core/Instances;)D", data.jobject)


def get_prc(data):
    """
    Calculates the area under the precision recall curve (PRC).
    :param data: the threshold curve data
    :type data: Instances
    :return: the area
    :rtype: float
    """
    return javabridge.static_call(
        "weka/classifiers/evaluation/ThresholdCurve", "getPRCArea", "(Lweka/core/Instances;)D", data.jobject)


def plot_roc(evaluation, class_index=None, title=None, key_loc="lower right", outfile=None, wait=True):
    """
    Plots the ROC (receiver operator characteristics) curve for the given predictions.
    TODO: click events http://matplotlib.org/examples/event_handling/data_browser.html
    :param evaluation: the evaluation to obtain the predictions from
    :type evaluation: Evaluation
    :param class_index: the list of 0-based indices of the class-labels to create the plot for
    :type class_index: list
    :param title: an optional title
    :type title: str
    :param key_loc: the position string for the key
    :type key_loc: str
    :param outfile: the output file, ignored if None
    :type outfile: str
    :param wait: whether to wait for the user to close the plot
    :type wait: bool
    """
    if not plot.matplotlib_available:
        logger.error("Matplotlib is not installed, plotting unavailable!")
        return
    if class_index is None:
        class_index = [0]
    ax = None
    for cindex in class_index:
        data = generate_thresholdcurve_data(evaluation, cindex)
        head = evaluation.header
        area = get_auc(data)
        x, y = get_thresholdcurve_data(data, "False Positive Rate", "True Positive Rate")
        if ax is None:
            fig, ax = plt.subplots()
            ax.set_xlabel("False Positive Rate")
            ax.set_ylabel("True Positive Rate")
            if title is None:
                title = "ROC"
            ax.set_title(title)
            ax.grid(True)
            fig.canvas.set_window_title(title)
            plt.xlim([-0.05, 1.05])
            plt.ylim([-0.05, 1.05])
        plot_label = head.class_attribute.value(cindex) + " (AUC: %0.4f)" % area
        ax.plot(x, y, label=plot_label)
        ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", c="0.3")
    plt.draw()
    plt.legend(loc=key_loc, shadow=True)
    if not outfile is None:
        plt.savefig(outfile)
    if wait:
        plt.show()


def plot_prc(evaluation, class_index=None, title=None, key_loc="lower center", outfile=None, wait=True):
    """
    Plots the PRC (precision recall) curve for the given predictions.
    TODO: click events http://matplotlib.org/examples/event_handling/data_browser.html
    :param evaluation: the evaluation to obtain the predictions from
    :type evaluation: Evaluation
    :param class_index: the list of 0-based indices of the class-labels to create the plot for
    :type class_index: list
    :param title: an optional title
    :type title: str
    :param key_loc: the location string for the key
    :type key_loc: str
    :param outfile: the output file, ignored if None
    :type outfile: str
    :param wait: whether to wait for the user to close the plot
    :type wait: bool
    """
    if not plot.matplotlib_available:
        logger.error("Matplotlib is not installed, plotting unavailable!")
        return
    if class_index is None:
        class_index = [0]
    ax = None
    for cindex in class_index:
        data = generate_thresholdcurve_data(evaluation, cindex)
        head = evaluation.header
        area = get_prc(data)
        x, y = get_thresholdcurve_data(data, "Recall", "Precision")
        if ax is None:
            fig, ax = plt.subplots()
            ax.set_xlabel("Recall")
            ax.set_ylabel("Precision")
            if title is None:
                title = "PRC"
            ax.set_title(title)
            fig.canvas.set_window_title(title)
            plt.xlim([-0.05, 1.05])
            plt.ylim([-0.05, 1.05])
            ax.grid(True)
        plot_label = head.class_attribute.value(cindex) + " (PRC: %0.4f)" % area
        ax.plot(x, y, label=plot_label)
        ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", c="0.3")
    plt.draw()
    plt.legend(loc=key_loc, shadow=True)
    if not outfile is None:
        plt.savefig(outfile)
    if wait:
        plt.show()
