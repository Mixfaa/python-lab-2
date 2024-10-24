import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# task 1
energy = pd.read_excel("En_In.xls", skiprows=17)
pd.set_option("future.no_silent_downcasting", True)
energy.drop(energy.columns[[0, 1]], axis=1, inplace=True)

energy.columns = ["Country", "Energy Supply", "Energy Supply per Capita", "% Renewable"]

# task 2
energy["Energy Supply"] = energy["Energy Supply"].replace(r"\.", np.nan, regex=True)
energy["Energy Supply"] *= 1000000

# task 3
to_rename = {
    "Republic of Korea": "South Korea",
    "United States of America": "United States",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "China, Hong Kong Special Administrative Region": "Hong Kong",
}
energy["Country"] = energy["Country"].replace(to_rename)

# task 4
energy["Country"] = (
    energy["Country"]
    .str.replace(r"\(.*\)|\d+", "", regex=True)
    .replace(r"\s+$", "", regex=True)
)

# print(energy.loc[energy["Country"].isin(["American Samoa", "South Korea", "Bolivia"])])


# task 5
gpd = pd.read_csv("gpd.csv", skiprows=4)

to_rename = {
    "Korea, Rep.": "South Korea",
    "Iran, Islamic Rep.": "Iran",
    "Hong Kong SAR, China": "Hong Kong",
}

gpd["Country Name"] = gpd["Country Name"].replace(to_rename)

# print(gpd.head(1))

# task 6
scimagojr = pd.read_excel("scimagojr.xlsx")

# task 7
scimagojr_top15 = scimagojr[scimagojr["Rank"] <= 15]

gpd.rename(columns={"Country Name": "Country"}, inplace=True)

gpd_2006_2015 = gpd[["Country"] + [str(year) for year in range(2006, 2016)]]
gpd_2006_2015_top15 = gpd_2006_2015[
    gpd_2006_2015["Country"].isin(scimagojr_top15["Country"])
]

energy_top15 = energy[energy["Country"].isin(scimagojr_top15["Country"])]

scimagojr_energy_merged = pd.merge(scimagojr, energy_top15, on="Country")
final_merged = pd.merge(scimagojr_energy_merged, gpd_2006_2015_top15, on="Country")
final_merged.set_index("Country", inplace=True)

# print(final_merged.head(3))
# print(final_merged.shape)
# print(final_merged.columns)


# task 8
def avg_gpd():
    return (
        final_merged[[str(year) for year in range(2006, 2016)]]
        .mean(axis=1)
        .sort_values(ascending=False)
    )


# print(avg_gpd())


# task 9
def gpd_delta():
    fifth_country = avg_gpd().index[4]
    gdp_2006 = final_merged.loc[fifth_country, "2006"]
    gdp_2015 = final_merged.loc[fifth_country, "2015"]
    gdp_change = gdp_2015 - gdp_2006
    return (fifth_country, gdp_change)


# print(gpd_delta())


# task 10
def max_renewable_percent():
    max_renewable_country = final_merged["% Renewable"].idxmax()
    return (
        max_renewable_country,
        final_merged.loc[max_renewable_country, "% Renewable"],
    )


# print(max_renewable_percent())


# task 11
def add_population():
    final_merged["Estimated population"] = final_merged["Energy Supply"] / final_merged["Energy Supply per Capita"].replace(0, np.nan)

def get_six_country_by_population():
    population_sorted = final_merged["Estimated population"].sort_values(
        ascending=False
    )
    sixth_country = population_sorted.index[5]
    sixth_population = population_sorted.iloc[5]
    return (sixth_country, sixth_population)


add_population()
# print(get_six_country_by_population())


# task 12
def add_citations_per_person():
    final_merged["Citations per Person"] = (
        final_merged["Citations"] / final_merged["Estimated population"]
    )

def get_correlation_task_12():
    correlation = final_merged["Citations per Person"].corr(final_merged["Energy Supply per Capita"])
    return correlation

add_citations_per_person()
# print(get_correlation_task_12())


# task 13
def add_renewable_above_median():
    median = final_merged["% Renewable"].median()
    final_merged["Renewable Above Median"] = (
        final_merged["% Renewable"] >= median
    ).astype(int)

def get_renewable_above_median_to_rank():
    return final_merged[["Renewable Above Median", "Rank"]].sort_values(by="Rank")

add_renewable_above_median()
# print(get_renewable_above_median_to_rank())


# task 14
сontinentDict = {
    "China": "Asia",
    "United States": "North America",
    "Japan": "Asia",
    "United Kingdom": "Europe",
    "Russian Federation": "Europe",
    "Canada": "North America",
    "Germany": "Europe",
    "India": "Asia",
    "France": "Europe",
    "South Korea": "Asia",
    "Italy": "Europe",
    "Spain": "Europe",
    "Iran": "Asia",
    "Australia": "Australia",
    "Brazil": "South America",
}

def add_continent():
    final_merged["Continent"] = final_merged.index.to_series().map(сontinentDict)

def groupby_continent():
    population_stats = final_merged.groupby("Continent")["Estimated population"].agg(
        ["size", "sum", "mean", "std"]
    )
    return population_stats

add_continent()
# print(groupby_continent())


# task 15
continent_colors = {
    "Asia": "red",
    "Europe": "green",
    "North America": "blue",
    "South America": "yellow",
    "Australia": "purple",
}


def show_chart():
    final_merged["Color"] = final_merged["Continent"].map(continent_colors)
    plt.figure(figsize=(10, 6))
    plt.scatter(
        final_merged["Rank"],
        final_merged["% Renewable"],
        s=final_merged["2015"] / 1000000000,  # Розмір бульбашки - ВВП за 2015 рік
        c=final_merged["Color"],
        alpha=0.6,
        edgecolor="w",
        linewidth=0.5,
    )
    plt.grid(True)
    plt.xlabel("Rank")
    plt.ylabel("% Renewable")
    plt.title("% Renewable vs. Rank (size by 2015 GDP, color by continent)")
    plt.show()

show_chart()
