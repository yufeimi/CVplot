import yaml
import os


class CVMetaData:
    def __init__(self, argv):
        print("Initializing data...")
        # Read the data
        if len(argv) > 1:
            self._filename = argv[1]
        else:
            self._filename = "./control_volume_analysis.csv"

        # Read config file
        self._open_glottis = [0.0, 1.0]
        working_dir = str()
        if len(argv) > 2:
            config_filename = argv[2]
        else:
            config_filename = self._filename.replace(
                "control_volume_analysis.csv", "plot_settings.yaml")
            working_dir = os.path.dirname(self.filename)
            print(working_dir)
        with open(config_filename) as plot_configs:
            self._documents = yaml.full_load(plot_configs)
            self._open_glottis[0] = self._documents["open phase"]
            self._open_glottis[1] = self._documents["close phase"]
            self._output_dir = os.path.join(
                working_dir, self._documents["output directory"])
            # Create dir if not exist
            if not os.path.exists(self._output_dir):
                print("Output directory doesn't exist, will create the directory...")
                os.mkdir(self._output_dir)
            self._timespan = self._documents["time span"]
            self._n_period = 1.0
            if "period" in self._documents:
                self._n_period = self._documents["period"]

            for item, doc in self._documents.items():
                print(item, ":", doc)

    @property
    def documents(self):
        return self._documents

    @property
    def open_glottis(self):
        return self._open_glottis

    @property
    def timespan(self):
        return self._timespan

    @property
    def filename(self):
        return self._filename

    @property
    def output_dir(self):
        return self._output_dir

    @property
    def n_period(self):
        return self._n_period