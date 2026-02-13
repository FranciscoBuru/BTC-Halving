import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

DATE0 = "2012-11-28"
DATE1 = "2016-07-09"
DATE2 = "2020-05-11"
DATE3 = "2024-04-19"
FILE_NAME = "./btc-usd-max.csv"
DATE_INDEX = "snapped_at"
PRICE = "price"

LABEL_INTERVAL_1 = "2013-2016"
LABEL_INTERVAL_2 = "2016-2020"
LABEL_INTERVAL_3 = "2020-2024"
LABEL_INTERVAL_4 = "2024-TODAY"

DAYS_BEFORE = 180
DAYS_AFTER = 530


def main():
    df1, df2, df3, df4 = read_file(FILE_NAME)
    halving_prices(df1, df2, df3, df4)
    halving_max_min_days(df1, df2, df3, df4)
    halving_days_before_after(df1, df2, df3, df4)
    normalized_graph(df1, df2, df3, df4)


# Prints max and min price per halving and the multiplier
def halving_prices(df1, df2, df3, df4):
    print_halve_index_data(df1, "------First Halving--------")
    print_halve_index_data(df2, "------Secnd Halving--------")
    print_halve_index_data(df3, "------Third Halving--------")
    print_halve_index_data(df4, "------Fourth Halving--------")
    print("-------------------------")


# Plots normalized prices in the intervals
# of [:DATE1], [DATE1:DATE2], [DATE2:]
def normalized_graph(df1, df2, df3, df4):
    # Normalizing per halving
    saved_max = df4.max()
    df1 = (df1 - df1.min()) / (df1.max() - df1.min())
    df2 = (df2 - df2.min()) / (df2.max() - df2.min())
    df3 = (df3 - df3.min()) / (df3.max() - df3.min())
    df4 = (df4 - df4.min()) / (df4.max() - df4.min())

    # Get the normalization value at the index equal to the length of df4
    # Use the last index of df4 as the index in df3
    target_index = len(df4) - 1
    # target_index = 547
    if len(df3) > target_index:  # Ensure df3 has enough elements
        target_value = df3.iloc[target_index]
    else:
        print("df3 has fewer elements than the length of df4.")
        return

    # Adjust df4 to match the target value at the specified index in df3
    scaling_factor = target_value / df4.max()
    df4 *= scaling_factor  # Apply the scaling to align df4
    print("ALOHA")
    x = 1 * scaling_factor * (df4.max() - df4.min()) + df4.min()
    print(saved_max/df4.max())

    df1, df2, df3, df4, prim, seg, ter, cuart, offset = drop_index_get_np_array(
        df1, df2, df3, df4)
    x = np.arange(ter.size)
    # Plot it all
    plt.plot(x, prim, label=LABEL_INTERVAL_1)
    plt.plot(x, seg, label=LABEL_INTERVAL_2)
    plt.plot(x, ter, label=LABEL_INTERVAL_3)
    plt.plot(x, cuart, label=LABEL_INTERVAL_4)
    plt.legend()
    plt.xlabel("Days After Halving")
    plt.ylabel("Normalized price")
    # plt.savefig("plt1.png")
    plt.show()


# Prints the day after halving wher the price was lowest or highest.
def halving_max_min_days(df1, df2, df3, df4):
    df1, df2, df3, df4, prim, seg, ter, cuart, offset = drop_index_get_np_array(
        df1, df2, df3, df4)
    min1, max1 = print_max_min_day_data(df1, offset, "blue: ")
    min2, max2 = print_max_min_day_data(df2, 0, "orange: ")
    min3, max3 = print_max_min_day_data(df3, 0, "green: ")
    min4, max4 = print_max_min_day_data(df4, 0, "purple: ")

    print("\nMultiplier between Maximums blue and orange: ",
          seg[max2] / prim[max1])
    print("Multiplier between Maximums orange and green: ",
          ter[max3] / seg[max2])


# Prints prices on DAYS_BEFORE halving and DAYS_AFTER halving.
# and the multiplier.
def halving_days_before_after(df1, df2, df3, df4):
    df1, df2, df3, df4, prim, seg, ter, cuart, offset = drop_index_get_np_array(
        df1, df2, df3, df4)
    print_prices_days_after_before(prim, seg, "first")
    print_prices_days_after_before(seg, ter, "second")
    print_prices_days_after_before(ter, cuart, "third")


# =============== Helper Functions ===============


def print_prices_days_after_before(first, second, text):
    print(f"\nDays after {text} halve: ")
    print(
        f" Price {DAYS_BEFORE} days before {text} halving: {
            first[first.size - DAYS_BEFORE]}"
    )
    print(f" Price {DAYS_AFTER} days after {text} halve: {second[DAYS_AFTER]}")
    print(f" Multiplier: {second[DAYS_AFTER] /
          first[first.size - DAYS_BEFORE]}")


def drop_index_get_np_array(df1, df2, df3, df4):
    df1 = df1.reset_index(drop=True)
    df2 = df2.reset_index(drop=True)
    df3 = df3.reset_index(drop=True)
    df4 = df4.reset_index(drop=True)
    # Adjust missing days, approximate
    prim = df1[PRICE].to_numpy()
    seg = df2[PRICE].to_numpy()
    ter = df3[PRICE].to_numpy()
    cuart = df4[PRICE].to_numpy()
    offset = seg.size - prim.size
    # Adjust lengths
    print(prim.size)
    print(seg.size)
    print(ter.size)
    print(cuart.size)
    print("Hola")
    prim = np.insert(prim, 0, np.zeros(ter.size - prim.size))
    seg = np.insert(seg, seg.size, np.zeros(ter.size - seg.size))
    cuart = np.insert(cuart, cuart.size, np.zeros(ter.size - cuart.size))
    prim[prim == 0] = np.nan
    # ter[ter == 0] = np.nan
    cuart[cuart == 0] = np.nan
    return df1, df2, df3, df4, prim, seg, ter, cuart, offset


def print_halve_index_data(df, text):
    print(f"\n{text}")
    print("Min: ", df[PRICE].min())
    print("Max: ", df[PRICE].max())
    print("Mul: ", df[PRICE].max() / df[PRICE].min())


def print_max_min_day_data(df, offset, text):
    print("\nMin ", text, df[PRICE].idxmin() + offset)
    print("Max ", text, df[PRICE].idxmax() + offset)
    return df[PRICE].idxmin() + offset, df[PRICE].idxmax() + offset


def read_file(name):
    data = pd.read_csv(name)
    # Data handling
    data = data[[DATE_INDEX, PRICE]]
    data[DATE_INDEX] = pd.to_datetime(data[DATE_INDEX])
    df = data.set_index([DATE_INDEX])
    df1 = df[:DATE1]
    df2 = df[DATE1:DATE2]
    df3 = df[DATE2:DATE3]
    df4 = df[DATE3:]
    return df1, df2, df3, df4


main()
