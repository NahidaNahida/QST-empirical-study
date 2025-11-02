import matplotlib.pyplot as plt

# Set Palatino Linotype font globally
plt.rcParams['font.family'] = 'Palatino Linotype'
plt.rcParams['text.usetex'] = False
# Configure mathtext (LaTeX) to use Palatino Linotype font as well
plt.rcParams['mathtext.fontset'] = 'custom'  # Use custom font set for mathtext
plt.rcParams['mathtext.rm'] = 'Palatino Linotype'  # Roman font (text)
plt.rcParams['mathtext.it'] = 'Palatino Linotype:italic'  # Italic font
plt.rcParams['mathtext.bf'] = 'Palatino Linotype:bold'  # Bold font