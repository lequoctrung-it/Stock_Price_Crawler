import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.utils import to_time_series_dataset

# Initialize constant variables and read data.csv
colors = {'red': '#ff207c', 'grey': '#42535b', 'blue': '#207cff', 'orange': '#ffa320', 'green': '#00ec8b'}
config_ticks = {'size': 14, 'color': colors['grey'], 'labelcolor': colors['grey']}
first_5_stock_symbols = ['DLG', 'GEG', 'VPB', 'TDH', 'TIX']
df = pd.read_csv('data.csv')


def normalized_stock_price(stock_name):
    # Open file data.csv as a pivot_table (not handle missing data)
    df_horizontal_symbols = pd.pivot_table(df,
                                           index='date',
                                           columns='stock_name',
                                           values='closing_price',
                                           aggfunc={
                                               'closing_price': lambda x: set(x).pop()
                                           })
    # Get stock price by symbol
    df1 = df_horizontal_symbols[stock_name]

    # scale data
    scaler = TimeSeriesScalerMeanVariance(mu=0.0, std=1.)
    scaled = scaler.fit_transform(to_time_series_dataset(df1))

    # format result to dataframe with 3 columns
    scaled = scaled.ravel()
    df2 = pd.DataFrame({"normalized": scaled})
    df1 = df1.to_frame()
    date = df_horizontal_symbols.index.to_frame()
    df1.index = date.index = df2.index
    return df1.join(df2).join(date)


# Charts formatter
def format_borders(plot):
    plot.spines['top'].set_visible(False)
    plot.spines['left'].set_visible(False)
    plot.spines['left'].set_color(colors['grey'])
    plot.spines['bottom'].set_color(colors['grey'])


def get_charts(stock_data, axs_outer, columns):
    date = stock_data['date']
    close = stock_data[columns]

    plot_price = axs_outer
    plot_price.plot(date, close, color=colors['blue'],
                    linewidth=2, label='Price')

    plot_price.yaxis.tick_right()
    plot_price.tick_params(axis='both', **config_ticks)
    plot_price.set_ylabel('Price (thousand VND)', fontsize=14)
    plot_price.yaxis.set_label_position("right")
    plot_price.yaxis.label.set_color(colors['grey'])
    plot_price.grid(axis='y', color='gainsboro',
                    linestyle='-', linewidth=0.5)
    for tick in plot_price.get_xticklabels():
        tick.set_rotation(45)
    plot_price.set_axisbelow(True)
    plot_price.set_title(columns)
    format_borders(plot_price)


def visualize_stock_price(symbol):
    norm_df = normalized_stock_price(symbol)
    norm_df = norm_df.astype({symbol: 'float', 'normalized': 'float', 'date': 'datetime64[ns]'}, copy=False)
    norm_df['date'] = pd.to_datetime(norm_df['date'], format="%d/%m/%Y")
    norm_df.sort_values(by='date', inplace=True, ascending=False)

    plt.close('all')
    fig = plt.figure()

    gs1 = gridspec.GridSpec(2, 1)
    ax1 = fig.add_subplot(gs1[0])
    ax2 = fig.add_subplot(gs1[1])

    get_charts(norm_df, ax1, symbol)
    get_charts(norm_df, ax2, 'normalized')

    gs1.tight_layout(fig)
    plt.show()


# Display 5 stock symbols before and after normalized
for i in first_5_stock_symbols:
    visualize_stock_price('VPB')