from django.shortcuts import render
from .models import Article
import pandas as pd
import numpy as np
import os
import glob
import plotly.offline as offline
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import cufflinks as cf


def article_detail(request, pk):
    article = Article.objects.get(pk=pk)
    return render(request, 'article_deatil.html', {'article': article})


def Characteristic(request):
    os.chdir("C:\\CSV")

    stats_table = []
    fig_table = []

    # glob.glob is used to iterate all the files in the current folde
    fileList = glob.glob('*.csv')

    for file in fileList:
        fileName = file.strip('.csv')

        df = pd.read_csv(file, header=12)  # skip first 12 rows
        # print(df.columns) #確認title用

        """
        由於(x,y)可能會重複，要將順序最後的(x,y)作為最終值。
        """
        df.drop_duplicates(
            subset=['ProberX#  ', 'ProberY#  '], keep='last', inplace=True)

        """
        sorting後去掉serier#, site#, probeX/Y# and Bin# information
        """
        df = df.iloc[:, 5:]  # data start from column 6
        # change non-numeric to NaN, which could be identified in python
        df = df.apply(pd.to_numeric, errors='coerce')

        par_num = len(df.columns)

        """
        計算各item的平均值以及標準差
        """
        frames = [df.mean(), df.std()]
        stats = pd.concat(frames, axis=1)
        stats.columns = ['AVG', 'STD']
        stats.index.name = 'Parameters'
        stats.insert(loc=0, column='File', value=fileName)

        s_out = stats.pivot_table(
            index='Parameters', columns='File').swaplevel(axis=1).sort_index(1)

        stats_table.append(s_out)

        """
        將所有file合併成為一large data frame (plot 前置)
        """
        df.index.name = 'Parameters'
        df.insert(loc=0, column='File', value=fileName)

        f_out = df.pivot_table(index='Parameters', columns='File').swaplevel(
            axis=1).sort_index(1)

        fig_table.append(f_out)

    """
    Export (至此統計表的部分已完成)
    """
    stats_table = pd.concat(stats_table, axis=1)
    fig_table = pd.concat(fig_table, axis=1)

    """
    根據fig_table作直條圖
    """

    cf.set_config_file(offline=True, world_readable=True, theme='ggplot')

    # print(fig_table.columns)
    # filename=fig_table.columns.levels[0][files]
    # parameter=fig_table.columns.levels[1][parameters]
    file_num = len(fileList)
    plot_div_array = []

    x = pd.DataFrame()
    for par in range(par_num):
        for file in range(file_num):
            x[fig_table.columns.levels[0][file]] = fig_table.loc[:,
                                                                 (fig_table.columns.levels[0][file], fig_table.columns.levels[1][par])]

        y = x.reset_index()['har']
        data = [go.Histogram(x=y)]
        plot_data = str(offline.plot(
            data,
            filename='test_{}.html'.format(par),
            auto_open=False,
            output_type='div',
        ))
        plot_div_array.append(plot_data)

    return render(request, 'article_list.html', {'data': plot_div_array})
    # x.iplot(kind='histogram', barmode='group',
    #         filename='test_{}.html'.format(par))
