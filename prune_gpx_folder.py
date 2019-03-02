"""
The script parses a set of GPX files from a directory and outputs a second set of
GPX files, with the goal of combining many small files into a number of larger files.
The combination is controlled by:
i) Maximum number of track points in a single  output file, i.e. a new output file will
    be created whenever this maximum is reached. See N_POINTS_PER_FILE
ii) Skipping track points in the input files. This allows a reduction in the total
    number of track points. See N_POINTS_TO_SKIP
"""
import math
from pathlib import Path
import gpxpy
import gpxpy.gpx

N_POINTS_PER_FILE = int(1e6) # number of points before starting a new output file
N_POINTS_TO_SKIP = 1 # e.g. for two we keep every second point in the output

# Input folder for reading GPX files:
# gpx_folder = Path('/home/fvdnabee/Documents/Garmin/History/Silk_road_2018/pruning')
gpx_folder = Path('/home/fvdnabee/Documents/Garmin/History/Zuid_Europa_2017/pruning')

def batch_to_xml(batch_points):
    # Create GPX file:
    gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for idx, p in enumerate(batch_points):
        if idx % N_POINTS_TO_SKIP == 0:
            # Create points:
            p.position_dilution = None # get rid of pdop output field in case of Locus generated GPX
            gpx_segment.points.append(p)

    gpx_xml = gpx.to_xml(version='1.0', prettyprint=False) # we use version 1.0 in order to get rid of any extensions. Together with prettyprint False this helps reduce file size

    return gpx_xml

if __name__ == "__main__":
    # Create output folder
    output_folder = gpx_folder / 'pruned'
    output_folder.mkdir(exist_ok=True)

    gpx_files = gpx_folder.glob('*.gpx')

    all_points = []
    print('Parsing GPX files in {}'.format(gpx_folder))
    for f in gpx_files:
        with open(f, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        all_points.append(point)

    # To return a new list, use the sorted() built-in function...
    all_points_sorted = sorted(all_points, key=lambda x: x.time, reverse=False)
    N = len(all_points_sorted)

    print('Counted {} points'.format(N))

    # Write points to files:
    print('Creating GPX files in {}, for batch_size = {} and N_POINTS_TO_SKIP = {}:'.format(output_folder, N_POINTS_PER_FILE, N_POINTS_TO_SKIP))

    for i in range(math.ceil(N/N_POINTS_PER_FILE)):
        # Create an output file i with one track that contains points [i, i + 1] * N_POINTS_PER_FILE
        if (i + 1)*N_POINTS_PER_FILE <= N:
            batch = all_points_sorted[i*N_POINTS_PER_FILE:(i+1)*N_POINTS_PER_FILE]
        else:
            batch = all_points_sorted[i*N_POINTS_PER_FILE:]

        batch_xml = batch_to_xml(batch)

        output_file_path = output_folder / "pruned-{:06d}.gpx".format(i)
        output_file_path.write_text(batch_xml)

        print('  Written batch {} ({}:{}) to file {}'.format(i, i*N_POINTS_PER_FILE, (i+1)*N_POINTS_PER_FILE, output_file_path))
