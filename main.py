# Purpose: Main Function - Training and Plotting Results
#
#   Info: Change the Parameters at the top of the scrip to change how the Agent interacts
#
#   Developed as part of the Software Agents Course at City University
#
#   Dev: Dan Dixey and Enrico Lopedoto
#
#   Updated: 1/3/2016
#
import logging
import os
import sys
from time import time
import json

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
from Model.Helicopter import helicopter
from Model import World as W
from Model.Plotting import plotting_model
import matplotlib.pyplot as plt
import numpy as np
from Settings import *
from Model import Utils
plt.style.use('ggplot')


# Logging Controls Level of Printing
logging.basicConfig(format='[%(asctime)s] : [%(levelname)s] : [%(message)s]',
                    level=logging.DEBUG)


logging.info("Setting Parameters:")
# Model Settings
case = 'case_three'
settings_ = case_lookup[case]
iterations, settings = get_indicies(settings_)

# Plot Settings
plot_settings = dict(print_up_to=-1,
                     end_range=list(range(settings['trials'],
                                          settings['trials'] + 1)),
                     print_rate=25)

logging.info("Load Helicopter and World")
HeliWorld = W.helicopter_world(file_name="Track_1.npy")
# file_name=None - Loads a Randomly Generated Track
Helicopter1 = helicopter(world=HeliWorld,
                         settings=settings)

logging.info("Starting the Learning Process")
st = time()
time_metrics = []

results = dict(time_chart=[],
               final_location=[],
               best_test=[],
               q_plot=[],
               model_names=[])

t_array = []  # Storing Time to Complete
f_array = []  # Storing Final Locations
b_array = []  # Storing Full Control
a = np.zeros(shape=(HeliWorld.track_height,
                    HeliWorld.track_width))

logging.info('Dealing with Case: {}'.format(case))
for value_iter in range(iterations):
    if value_iter > 0:
        settings = get_settings(dictionary=settings_,
                                ind=value_iter)
        HeliWorld = W.helicopter_world(file_name="Track_1.npy")
        Helicopter1 = helicopter(world=HeliWorld,
                                 settings=settings)
        a = np.zeros(shape=(HeliWorld.track_height,
                            HeliWorld.track_width))
        t_array = []  # Storing Time to Complete
        f_array = []  # Storing Final Locations
        b_array = []  # Storing Full Control
        q_array = []  # Storing Q Array
        logging.info('Changing Values: {}'.format(settings_['change_values']))

    while HeliWorld.trials <= settings['trials']:
        # On the Last Trail give the Model full control
        if HeliWorld.trials == settings['trials']:
            Helicopter1.ai.epsilon, settings['epsilon'] = 1e-9, 1e-9

        # Print out logging metrics
        if HeliWorld.trials % plot_settings[
                'print_rate'] == 0 and HeliWorld.trials > 0:
            rate = ((time() - st + 0.01) / HeliWorld.trials)
            value = [HeliWorld.trials, rate]
            time_metrics.append(value)
            logging.info(
                "Trials Completed: {} at {:.4f} seconds / trial".format(value[0], value[1]))

        # Inner loop of episodes
        while True:
            output = Helicopter1.update()
            if HeliWorld.trials == settings['trials']:
                b_array.append(Helicopter1.current_location)
            if not output:
                f_array.append(
                    [HeliWorld.trials, Helicopter1.current_location[0]])
                Helicopter1.reset()
                rate = (time() - st + 0.01) / HeliWorld.trials
                value = [HeliWorld.trials,
                         rate]
                t_array.append(value)
                break

            if HeliWorld.trials <= plot_settings[
                    'print_up_to'] or HeliWorld.trials in plot_settings['end_range']:
                # Primary Title
                rate = (time() - st + 0.01) / HeliWorld.trials
                value = [HeliWorld.trials,
                         rate]

            pos, array_masked = Helicopter1.return_q_view()
            a[:, pos - 1] += array_masked

        logging.debug('Starting next iteration')
        HeliWorld.trials += 1

    name = 'alpha_{}_epsilon_{}_gamma_{}_trails_{}_nb_actions_{}_model_{}_case_{}'.format(
        settings['alpha'],
        settings['epsilon'],
        settings['gamma'],
        settings['trials'],
        settings['nb_actions'],
        settings['model'],
        case)

    # Record Results
    results['time_chart'].append(t_array),
    results['final_location'].append(f_array)
    results['best_test'].append(b_array)
    results['q_plot'].append(a.tolist())
    results['model_names'].append(name)

    et = time()
    logging.info(
        "Time Taken: {} seconds for Iteration {}".format(
            et - st, value_iter + 1))

    if settings['model'] < 4:
        logging.info("Plotting the Q-Matrix")
        model_plot = plotting_model()
        model_plot.get_q_matrix(model_q=Helicopter1.ai.q,
                                nb_actions=settings['nb_actions'])
        model_plot.plot_q_matrix('Q-Matrix - {}'.format(name))
    else:
        # Saving the Neural Net Weights and Architecture
        Helicopter1.ai.save_model(name=name)

# Save all results to a JSON file
f = open(
    os.path.join(
        os.getcwd(),
        'Results',
        case,
        'Model{}'.format(
            settings['model']) +
        '.json'),
    'w').write(
    json.dumps(results))
