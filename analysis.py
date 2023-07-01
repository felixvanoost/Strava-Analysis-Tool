"""analysis.py

Processes and analyses Strava athlete and activity data.

Functions:
display_summary_statistics()
display_commute_statistics()
display_commute_plots()
display_activity_count_plot()
display_mean_distance_plot()
display_moving_time_heatmap()
display_start_country_plot()

Felix van Oost 2021
"""

# Third-party
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def _generate_moving_time_heatmap(*args, **kwargs):
    """
    Generate a heatmap of moving time for a single activity type.
    """
    data = kwargs.pop('data')
    sns.heatmap(data.pivot(index=args[1], columns=args[0], values=args[2]), **kwargs)


def _generate_start_country_plot(activity_data: pd.DataFrame, ax: mpl.axes.Axes,
                                 colour_palette: list):
    """
    Generate a bar plot of the number of activities started in each country (by
    type).

    Arguments:
    activity data - A pandas DataFrame containing the activity data.
    ax - A set of matplotlib axes to generate the plot on.
    colour_palette - The colour palette to generate the plot with.
    """

    data = activity_data.groupby(['country', 'type']).size().to_frame('count').reset_index()

    # Generate and format the bar plot
    sns.barplot(x='country',
                y='count',
                hue='type',
                data=data,
                palette=colour_palette,
                ax=ax)
    ax.set(title='Activities by country', ylabel='Number of activities', xlabel='Country')
    ax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
    ax.grid(b=True, which='major', linewidth=1.0)
    ax.yaxis.grid(b=True, which='minor', linewidth=0.5)
    ax.set_axisbelow(True)


def _generate_mean_distance_plot(activity_data: pd.DataFrame, ax: mpl.axes.Axes,
                                 colour_palette: list):
    """
    Generate a bar plot of mean activity distance over time (by type).

    Arguments:
    activity data - A pandas DataFrame containing the activity data.
    ax - A set of matplotlib axes to generate the plot on.
    colour_palette - The colour palette to generate the plot with.
    """

    # Group the activity data by month and calculate the mean distance of each activity type
    data = activity_data.groupby([activity_data.index.to_period('Y'), 'type']).mean().reset_index()

    # Generate and format the bar plot
    sns.barplot(x='start_date_local',
                y='distance',
                hue='type',
                data=data,
                palette=colour_palette,
                ax=ax)
    ax.set(title='Mean activity distance over time', ylabel='Mean distance (km)', xlabel='Year')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
    ax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(b=True, which='major', linewidth=1.0)
    ax.yaxis.grid(b=True, which='minor', linewidth=0.5)
    ax.set_axisbelow(True)


def _generate_activity_count_plot(activity_data: pd.DataFrame, ax: mpl.axes.Axes,
                                  colour_palette: list):
    """
    Generate a bar plot of activity counts over time (by type).

    Arguments:
    activity data - A pandas DataFrame containing the activity data.
    ax - A set of matplotlib axes to generate the plot on.
    colour_palette - The colour palette to generate the plot with.
    """

    # Group the activity data by month and calculate the count of each activity type
    data = (activity_data.groupby([activity_data.index.to_period('M'), 'type'])
            .size().to_frame('count').reset_index())

    # Generate and format the bar plot
    sns.lineplot(x=data['start_date_local'].astype(str),
                 y=data['count'],
                 hue=data['type'],
                 palette=colour_palette,
                 ax=ax)
    ax.set(title='Activities over time', ylabel='Number of activities', xlabel='Month')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
    ax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(b=True, which='major', linewidth=1.0)
    ax.yaxis.grid(b=True, which='minor', linewidth=0.5)
    ax.set_axisbelow(True)


def _generate_commute_count_plot(commute_data: pd.DataFrame, ax: mpl.axes.Axes,
                                 colour_palette: list):
    """
    Generate a bar plot of number of commutes per month.

    Arguments:
    commute_data - A pandas DataFrame containing the commute activity data.
    ax - A set of matplotlib axes to generate the plot on.
    colour_palette - The colour palette to generate the plot with.
    """

    # Group the commute data by month
    data = commute_data.resample('M').count()

    # Generate and format the bar plot
    sns.barplot(x=data.index.to_period('M'),
                y=data['distance'],
                color=colour_palette[0],
                ax=ax)
    ax.set(ylabel='Number of commutes', xlabel='Month')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
    ax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(b=True, which='major', linewidth=1.0)
    ax.yaxis.grid(b=True, which='minor', linewidth=0.5)
    ax.set_axisbelow(True)


def _generate_commute_distance_plot(commute_data: pd.DataFrame, ax: mpl.axes.Axes,
                                    colour_palette: list):
    """
    Generate a line plot of total and mean commute distance per year.

    Arguments:
    commute_data - A pandas DataFrame containing the commute activity data.
    ax - A set of matplotlib axes to generate the plot on.
    colour_palette - The colour palette to generate the plot with.
    """

    # Group the commute data by year
    data = commute_data.resample('Y').agg({'distance': ['sum', 'mean']})

    # Generate and format the total distance line plot
    sns.lineplot(x=data.index.year,
                 y=data['distance', 'sum'],
                 color=colour_palette[0],
                 marker='o',
                 ax=ax)
    ax.set_xlabel('Year')
    ax.set_ylabel('Total commute distance (km)', color=colour_palette[0])
    ax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(b=True, which='major', linewidth=1.0)
    ax.yaxis.grid(b=True, which='minor', linewidth=0.5)

    # Generate and format the mean distance line plot
    ax_mean = ax.twinx()
    sns.lineplot(x=data.index.year,
                 y=data['distance', 'mean'],
                 color=colour_palette[1],
                 marker='o',
                 ax=ax_mean)
    ax_mean.set_ylabel('Average commute distance (km)', color=colour_palette[1])


def _generate_commute_days_plot(commute_data: pd.DataFrame, ax: mpl.axes.Axes,
                                colour_palette: list):
    """
    Generate a line plot of commute days per year.

    Arguments:
    commute_data - A pandas DataFrame containing the commute activity data.
    ax - A set of matplotlib axes to generate the plot on.
    colour_palette - The colour palette to generate the plot with.
    """

    # Group the commute data by day
    data = commute_data.groupby(commute_data.index.to_period('D')).agg({'distance': 'mean'})

    # Generate and format the line plot
    sns.lineplot(x=data.index.year.value_counts().index,
                 y=data.index.year.value_counts(),
                 palette=colour_palette,
                 marker='o',
                 ax=ax)
    ax.set(ylabel='Commute days', xlabel='Year')
    ax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(b=True, which='major', linewidth=1.0)
    ax.yaxis.grid(b=True, which='minor', linewidth=0.5)


def _generate_commute_statistics(x: pd.Series) -> pd.Series:
    """
    Generate basic commute statistics from a given pandas Series.

    Arguments:
    x - The Series to generate basic commute statistics from.

    Return:
    A Series containing the following commute statistics:
    - Number of commutes
    - Total and average commute distance
    - Total and average commute time
    """

    rows = {'Number of commutes': x['type'].count(),
            'Total commute distance (km)': x['distance'].sum() / 1000,
            'Average commute distance (km)': x['distance'].mean() / 1000,
            'Total commute moving time (hours)': x['moving_time'].sum() / 3600,
            'Average commute moving time (mins)': x['moving_time'].mean() / 60}

    series = pd.Series(rows, index=['Number of commutes',
                                    'Total commute distance (km)',
                                    'Average commute distance (km)',
                                    'Total commute moving time (hours)',
                                    'Average commute moving time (mins)'])

    return series


def _generate_summary_statistics(x: pd.Series) -> pd.Series:
    """
    Generate basic statistics from a given pandas Series.

    Arguments:
    x - The Series to generate basic commute statistics from.

    Return:
    A Series containing the following statistics:
    - Total and average distance
    - Total and average moving time
    - Total and average elevation gain
    - Average speed
    """

    rows = {'Number of activities': x['type'].count(),
            'Total distance (km)': x['distance'].sum() / 1000,
            'Average distance (km)': x['distance'].mean() / 1000,
            'Total moving time (hours)': x['moving_time'].sum() / 3600,
            'Average moving time (mins)': x['moving_time'].mean() / 60,
            'Total elevation gain (km)': x['total_elevation_gain'].sum() / 1000,
            'Average elevation gain (m)': x['total_elevation_gain'].mean(),
            'Average speed (km/h)': (x['distance'].sum() / x['moving_time'].sum()) * 3.6}

    series = pd.Series(rows, index=['Number of activities',
                                    'Total distance (km)',
                                    'Average distance (km)',
                                    'Total moving time (hours)',
                                    'Average moving time (mins)',
                                    'Total elevation gain (km)',
                                    'Average elevation gain (m)',
                                    'Average speed (km/h)'])

    return series


def display_start_country_plot(activity_df: pd.DataFrame, colour_palette: list):
    """
    Generate and display a bar plot of the number of activities started in each
    country (by type).

    Arguments:
    activity_df - A pandas DataFrame containing the activity data.
    colour_palette - The colour palette to generate the heatmap with.
    """

    # TODO: Exclude virtual activities

    # Get the activity start address and extract the country from the dictionary
    activity_df['country'] = pd.DataFrame(activity_df['start_address']
                             .apply(lambda row: row['country'] if 'country' in row else None))

    activity_data = activity_df[['type', 'country']].copy()

    # Create an empty set of axes
    fig = plt.figure()
    fig.set_tight_layout(True)
    ax = fig.add_subplot(1, 1, 1)

    # Generate and display the plot
    _generate_start_country_plot(activity_data, ax, colour_palette)
    plt.show()


def display_moving_time_heatmap(activity_df: pd.DataFrame, colour_palette: list,
                                heatmap_column_wrap: int):
    """
    Generate and display a heatmap of activity moving time over time (by type).

    Arguments:
    activity_df - A pandas DataFrame containing the activity data.
    colour_palette - The colour palette to generate the heatmap with.
    """

    activity_data = activity_df[['type', 'moving_time', 'start_date_local']].copy()

    # Convert the activity moving times from seconds to hours
    activity_data.loc[:, 'moving_time'] = activity_data.loc[:, 'moving_time'] / 3600

    # Get the range of activity start years and unique activity types in the data set
    year_min = activity_data['start_date_local'].dt.year.min()
    year_max = activity_data['start_date_local'].dt.year.max()
    types = activity_data['type'].unique()

    # Extract the activity start year and month from the start dates
    activity_data.loc[:, 'year'] = activity_data['start_date_local'].dt.year
    activity_data.loc[:, 'month'] = activity_data['start_date_local'].dt.month

    # Group the activity data by activity type, year, and month
    activity_data = activity_data.groupby(['type', 'year', 'month']).sum().reset_index()
    activity_data = activity_data.set_index(['type', 'year', 'month'])

    # Fill in missing values in the activity data
    years = np.arange(year_min, year_max + 1, dtype=np.int)
    months = np.arange(1, 12 + 1, dtype=np.int)
    activity_data = activity_data.reindex(index=pd.MultiIndex.from_product([types, years, months],
                                          names=activity_data.index.names),
                                          fill_value=0)
    activity_data = activity_data.reset_index()

    # Create and plot a FacetGrid of heatmaps grouped by activity type
    fg = sns.FacetGrid(activity_data, col='type', col_wrap=heatmap_column_wrap)
    fg = fg.map_dataframe(_generate_moving_time_heatmap, 'year', 'month', 'moving_time',
                          annot=True, cbar=True, cmap=colour_palette)
    plt.show()


def display_mean_distance_plot(activity_df: pd.DataFrame, colour_palette: list):
    """
    Generate and display a bar plot of mean activity distance over time (by type).

    Arguments:
    activity_df - A pandas DataFrame containing the activity data.
    colour_palette - The colour palette to generate the plot with.
    """

    # Create a list of stationary activities to exclude from the plot
    exclude_list = ['Crossfit', 'RockClimbing', 'WeightTraining', 'Workout', 'Yoga']

    # Get only the activity distances, types, and start dates
    activity_data = (activity_df[~activity_df['type'].isin(exclude_list)]
                     [['distance', 'type', 'start_date_local']])
    activity_data = activity_data.set_index('start_date_local')

    # Convert the activity distances from m to km
    activity_data.loc[:, 'distance'] = activity_data.loc[:, 'distance'] / 1000

    # Create an empty set of axes
    fig = plt.figure()
    fig.set_tight_layout(True)
    ax = fig.add_subplot(1, 1, 1)

    # Generate and display the plot
    _generate_mean_distance_plot(activity_data, ax, colour_palette)
    plt.show()


def display_activity_count_plot(activity_df: pd.DataFrame, colour_palette: list):
    """
    Generate and display a bar plot of activity counts over time (by type).

    Arguments:
    activity_df - A pandas DataFrame containing the activity data.
    colour_palette - The colour palette to generate the plot with.
    """

    # Get only the activity types and start dates
    activity_data = activity_df[['type', 'start_date_local']]
    activity_data = activity_data.set_index('start_date_local')

    # Create an empty set of axes
    fig = plt.figure()
    fig.set_tight_layout(True)
    ax = fig.add_subplot(1, 1, 1)

    # Generate and display the plot
    _generate_activity_count_plot(activity_data, ax, colour_palette)
    plt.show()


def display_commute_plots(activity_df: pd.DataFrame, colour_palette: list):
    """
    Generate and display the following plots using data from activities
    marked as commutes:

    - Number of commute days per year (line plot)
    - Total and average commute distance per year (line plot)
    - Number of commutes per month (bar plot)

    Arguments:
    activity_df - A pandas DataFrame containing the activity data.
    colour_palette - The colour palette to generate the plot with.
    """

    # Get only commute data
    commute_data = (activity_df[activity_df['commute'] == True]
                    [['distance', 'start_date_local']])

    if commute_data.empty:
        return None

    commute_data = commute_data.set_index('start_date_local')

    # Convert the activity distances from m to km
    commute_data.loc[:, 'distance'] = commute_data.loc[:, 'distance'] / 1000

    # Create a new grid of subplots
    ax1 = plt.subplot2grid((2, 2), (0, 0), rowspan=1, colspan=1)
    ax2 = plt.subplot2grid((2, 2), (0, 1), rowspan=1, colspan=1)
    ax3 = plt.subplot2grid((2, 2), (1, 0), rowspan=1, colspan=2)

    # Format the global plot
    plt.suptitle('Commutes', size=16)

    # Generate and display the plots
    _generate_commute_days_plot(commute_data, ax1, colour_palette)
    _generate_commute_distance_plot(commute_data, ax2, colour_palette)
    _generate_commute_count_plot(commute_data, ax3, colour_palette)
    plt.show()


def display_commute_statistics(activity_df: pd.DataFrame):
    """
    Display basic commute statistics for each activity type.

    Arguments:
    activity_df - A pandas DataFrame containing the activity data.
    """

    commute_df = activity_df[activity_df['commute'] == True]

    if not commute_df.empty:
        commute_statistics = commute_df.groupby('type').apply(_generate_commute_statistics)

        print('Commute statistics:')
        print()
        print(commute_statistics.T)
        print()
    else:
        print('[Analysis]: No commutes found')


def display_summary_statistics(activity_df: pd.DataFrame):
    """
    Display basic statistics for each activity type.

    Arguments:
    activity_df - A pandas DataFrame containing the activity data.
    """

    if not activity_df.empty:
        summary_statistics = activity_df.groupby('type').apply(_generate_summary_statistics)

        print()
        print('Summary statistics:')
        print()
        print(summary_statistics.T)
        print()
    else:
        print('[Analysis]: No activities found')
