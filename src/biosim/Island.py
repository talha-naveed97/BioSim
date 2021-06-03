from .Cells import Water, Lowland, Highland, Desert


class Island:
    def __init__(self, geo):
        self.geo = geo
        self.cell_list = []

    def make_map(self):
        map_list = self.geo.splitlines()
        rows = len(map_list)
        for x in range(1, rows + 1):
            line = map_list[x - 1].strip()
            chars = len(line)
            cell = None
            for char in range(1, chars + 1):
                land_type = line[char - 1]
                print(x, char)
                loc = (x, char)
                if land_type == 'W':
                    cell = Water(loc)
                elif land_type == 'H':
                    cell = Highland(loc)
                elif land_type == 'L':
                    cell = Lowland(loc)
                elif land_type == 'D':
                    cell = Desert(loc)
                self.cell_list.append(cell)
