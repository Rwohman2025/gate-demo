def average(values):
    """Return the arithmetic mean of a list of numbers."""
    return sum(values) / len(values)


def main():
    values = []
    for i in range(10):
        values.append(float(input(f"Enter value {i + 1} of 10: ")))
    print(f"Average: {average(values)}")


if __name__ == "__main__":
    main()
