import os
import wx
import copy
from .._base import BaseComponent, Param, _translate
from psychopy import logging
from psychopy.tools.versionchooser import versionOptions, availableVersions

from psychopy.app.builder.experiment import _numpyImports, _numpyRandomImports

def readTextFile(relPath):
    fullPath = os.path.join(thisFolder, relPath)
    with open(fullPath, "r") as f:
        txt = f.read()
    return txt

# this is not a standard component - it will appear on toolbar not in
# components panel

# only use _localized values for label values, nothing functional:
_localized = {'expName': _translate("Experiment name"),
              'Show info dlg':  _translate("Show info dialog"),
              'Enable Escape':  _translate("Enable Escape key"),
              'Experiment info':  _translate("Experiment info"),
              'Data filename':  _translate("Data filename"),
              'Full-screen window':  _translate("Full-screen window"),
              'Window size (pixels)':  _translate("Window size (pixels)"),
              'Screen': _translate('Screen'),
              'Monitor':  _translate("Monitor"),
              'color': _translate("Color"),
              'colorSpace':  _translate("Color space"),
              'Units':  _translate("Units"),
              'blendMode':   _translate("Blend mode"),
              'Show mouse':  _translate("Show mouse"),
              'Save log file':  _translate("Save log file"),
              'Save wide csv file':
                  _translate("Save csv file (trial-by-trial)"),
              'Save csv file': _translate("Save csv file (summaries)"),
              'Save excel file':  _translate("Save excel file"),
              'Save psydat file':  _translate("Save psydat file"),
              'logging level': _translate("Logging level"),
              'Use version': _translate("Use PsychoPy version")}

thisFolder = os.path.split(__file__)[0]

class SettingsComponent(object):
    """This component stores general info about how to run the experiment
    """

    def __init__(self, parentName, exp, expName='', fullScr=True,
                 winSize=(1024, 768), screen=1, monitor='testMonitor',
                 showMouse=False, saveLogFile=True, showExpInfo=True,
                 expInfo="{'participant':'', 'session':'001'}",
                 units='use prefs', logging='exp',
                 color='$[0,0,0]', colorSpace='rgb', enableEscape=True,
                 blendMode='avg',
                 saveXLSXFile=False, saveCSVFile=False,
                 saveWideCSVFile=True, savePsydatFile=True,
                 savedDataFolder='',
                 useVersion='latest',
                 useIoHub=False,  # but set this to True anytime as new default
                 useHDF5 = False,
                 ioHubConfigFile = "iohub_config.yaml",
                 filename=None):
        self.type = 'Settings'
        self.exp = exp  # so we can access the experiment if necess
        self.exp.requirePsychopyLibs(['visual', 'gui'])
        self.parentName = parentName
        self.url = "http://www.psychopy.org/builder/settings.html"

        # if filename is the default value fetch the builder pref for the
        # folder instead
        if filename is None:
            filename = ("u'xxxx/%s_%s_%s' % (expInfo['participant'], expName,"
                        " expInfo['date'])")
        if filename.startswith("u'xxxx"):
            folder = self.exp.prefsBuilder['savedDataFolder'].strip()
            filename = filename.replace("xxxx", folder)

        # params
        self.params = {}
        self.order = ['expName', 'Show info dlg', 'Experiment info',
                      'Data filename',
                      'Save excel file', 'Save csv file',
                      'Save wide csv file', 'Save psydat file',
                      'Save log file', 'logging level',
                      'Monitor', 'Screen', 'Full-screen window',
                      'Window size (pixels)',
                      'color', 'colorSpace', 'Units',
                      'useIoHub', 'useHDF5', 'ioHubConfigFile',]
        # basic params
        self.params['expName'] = Param(
            expName, valType='str', allowedTypes=[],
            hint=_translate("Name of the entire experiment (taken by default"
                            " from the filename on save)"),
            label=_localized["expName"])
        self.params['Show info dlg'] = Param(
            showExpInfo, valType='bool', allowedTypes=[],
            hint=_translate("Start the experiment with a dialog to set info"
                            " (e.g.participant or condition)"),
            label=_localized["Show info dlg"], categ='Basic')
        self.params['Enable Escape'] = Param(
            enableEscape, valType='bool', allowedTypes=[],
            hint=_translate("Enable the <esc> key, to allow subjects to quit"
                            " / break out of the experiment"),
            label=_localized["Enable Escape"])
        self.params['Experiment info'] = Param(
            expInfo, valType='code', allowedTypes=[],
            hint=_translate("The info to present in a dialog box. Right-click"
                            " to check syntax and preview the dialog box."),
            label=_localized["Experiment info"], categ='Basic')
        self.params['Use version'] = Param(
            useVersion, valType='str',
            # search for options locally only by default, otherwise sluggish
            allowedVals=versionOptions() + [''] + availableVersions(),
            hint=_translate("The version of PsychoPy to use when running "
                            "the experiment."),
            label=_localized["Use version"], categ='Basic')

        # screen params
        self.params['Full-screen window'] = Param(
            fullScr, valType='bool', allowedTypes=[],
            hint=_translate("Run the experiment full-screen (recommended)"),
            label=_localized["Full-screen window"], categ='Screen')
        self.params['Window size (pixels)'] = Param(
            winSize, valType='code', allowedTypes=[],
            hint=_translate("Size of window (if not fullscreen)"),
            label=_localized["Window size (pixels)"], categ='Screen')
        self.params['Screen'] = Param(
            screen, valType='num', allowedTypes=[],
            hint=_translate("Which physical screen to run on (1 or 2)"),
            label=_localized["Screen"], categ='Screen')
        self.params['Monitor'] = Param(
            monitor, valType='str', allowedTypes=[],
            hint=_translate("Name of the monitor (from Monitor Center). Right"
                            "-click to go there, then copy & paste a monitor "
                            "name here."),
            label=_localized["Monitor"], categ="Screen")
        self.params['color'] = Param(
            color, valType='str', allowedTypes=[],
            hint=_translate("Color of the screen (e.g. black, $[1.0,1.0,1.0],"
                            " $variable. Right-click to bring up a "
                            "color-picker.)"),
            label=_localized["color"], categ='Screen')
        self.params['colorSpace'] = Param(
            colorSpace, valType='str',
            hint=_translate("Needed if color is defined numerically (see "
                            "PsychoPy documentation on color spaces)"),
            allowedVals=['rgb', 'dkl', 'lms', 'hsv'],
            label=_localized["colorSpace"], categ="Screen")
        self.params['Units'] = Param(
            units, valType='str', allowedTypes=[],
            allowedVals=['use prefs', 'deg', 'pix', 'cm', 'norm', 'height',
                         'degFlatPos', 'degFlat'],
            hint=_translate("Units to use for window/stimulus coordinates "
                            "(e.g. cm, pix, deg)"),
            label=_localized["Units"], categ='Screen')
        self.params['blendMode'] = Param(
            blendMode, valType='str',
            allowedTypes=[], allowedVals=['add', 'avg'],
            hint=_translate("Should new stimuli be added or averaged with "
                            "the stimuli that have been drawn already"),
            label=_localized["blendMode"], categ='Screen')
        self.params['Show mouse'] = Param(
            showMouse, valType='bool', allowedTypes=[],
            hint=_translate("Should the mouse be visible on screen?"),
            label=_localized["Show mouse"], categ='Screen')

        # data params
        self.params['Data filename'] = Param(
            filename, valType='code', allowedTypes=[],
            hint=_translate("Code to create your custom file name base. Don"
                            "'t give a file extension - this will be added."),
            label=_localized["Data filename"], categ='Data')
        self.params['Save log file'] = Param(
            saveLogFile, valType='bool', allowedTypes=[],
            hint=_translate("Save a detailed log (more detailed than the "
                            "excel/csv files) of the entire experiment"),
            label=_localized["Save log file"], categ='Data')
        self.params['Save wide csv file'] = Param(
            saveWideCSVFile, valType='bool', allowedTypes=[],
            hint=_translate("Save data from loops in comma-separated-value "
                            "(.csv) format for maximum portability"),
            label=_localized["Save wide csv file"], categ='Data')
        self.params['Save csv file'] = Param(
            saveCSVFile, valType='bool', allowedTypes=[],
            hint=_translate("Save data from loops in comma-separated-value "
                            "(.csv) format for maximum portability"),
            label=_localized["Save csv file"], categ='Data')
        self.params['Save excel file'] = Param(
            saveXLSXFile, valType='bool', allowedTypes=[],
            hint=_translate("Save data from loops in Excel (.xlsx) format"),
            label=_localized["Save excel file"], categ='Data')
        self.params['Save psydat file'] = Param(
            savePsydatFile, valType='bool', allowedVals=[True],
            hint=_translate("Save data from loops in psydat format. This is "
                            "useful for python programmers to generate "
                            "analysis scripts."),
            label=_localized["Save psydat file"], categ='Data')
        self.params['logging level'] = Param(
            logging, valType='code',
            allowedVals=['error', 'warning', 'data', 'exp', 'info', 'debug'],
            hint=_translate("How much output do you want in the log files? "
                            "('error' is fewest messages, 'debug' is most)"),
            label=_localized["logging level"], categ='Data')

        #  iohub params
        self.params['useIoHub'] = Param(
            useIoHub, valType='bool',
            allowedVals=[True, False],
            hint=_translate("Start ioHub for advanced hardware polling"),
            label=_translate('Use ioHub'), categ='ioHub')
        self.params['useHDF5'] = Param(
            useHDF5, valType='bool',
            allowedVals=[True, False],
            hint=_translate("Save data from ioHub using std file name"),
            label=_translate('Save HDF5 file'), categ='ioHub')
        self.params['ioHubConfigFile'] = Param(
            ioHubConfigFile, valType='str',
            hint=_translate("Config files contain info about your set up"),
            label=_translate('Config file (yaml)'), categ='ioHub')

    def getType(self):
        return self.__class__.__name__

    def getShortType(self):
        return self.getType().replace('Component', '')

    def getSaveDataDir(self):
        if 'Saved data folder' in self.params:
            # we have a param for the folder (deprecated since 1.80)
            saveToDir = self.params['Saved data folder'].val.strip()
            if not saveToDir:  # it was blank so try preferences
                saveToDir = self.exp.prefsBuilder['savedDataFolder'].strip()
        else:
            saveToDir = os.path.dirname(self.params['Data filename'].val)
        return saveToDir or u'data'

    def writeUseVersion(self, buff):
        if self.params['Use version'].val:
            code = ('\nimport psychopy\n'
                    'psychopy.useVersion({})\n\n')
            val = repr(self.params['Use version'].val)
            buff.writeIndentedLines(code.format(val))

    def writeInitCode(self, buff, version, localDateTime):

        buff.write(
            '#!/usr/bin/env python2\n'
            '# -*- coding: utf-8 -*-\n'
            '"""\nThis experiment was created using PsychoPy2 Experiment '
            'Builder (v%s),\n'
            '    on %s\n' % (version, localDateTime) +
            'If you publish work using this script please cite the PsychoPy '
            'publications:\n'
            '    Peirce, JW (2007) PsychoPy - Psychophysics software in '
            'Python.\n'
            '        Journal of Neuroscience Methods, 162(1-2), 8-13.\n'
            '    Peirce, JW (2009) Generating stimuli for neuroscience using '
            'PsychoPy.\n'
            '        Frontiers in Neuroinformatics, 2:10. doi: 10.3389/'
            'neuro.11.010.2008\n"""\n'
            "\nfrom __future__ import absolute_import, division\n")

        self.writeUseVersion(buff)

        buff.write(
            "from psychopy import locale_setup, "
            "%s\n" % ', '.join(self.exp.psychopyLibs) +
            "from psychopy.constants import (NOT_STARTED, STARTED, PLAYING,"
            " PAUSED,\n"
            "                                STOPPED, FINISHED, PRESSED, "
            "RELEASED, FOREVER)\n"
            "import numpy as np  # whole numpy lib is available, "
            "prepend 'np.'\n"
            "from numpy import (%s,\n" % ', '.join(_numpyImports[:7]) +
            "                   %s)\n" % ', '.join(_numpyImports[7:]) +
            "from numpy.random import %s\n" % ', '.join(_numpyRandomImports) +
            "import os  # handy system and path functions\n" +
            "import sys  # to get file system encoding\n")

        # This does not seem to work:
        #     if "iohub" in self.exp.psychopyLibs:
        # so using this instead for now:
        if self.params['useIoHub'].val:
             buff.write("\n# include ioHub imports\n"
                        "from psychopy.iohub.client import launchHubServer\n"
                        "\n")

    def writeInitCodeJS(self, buff, version, localDateTime):
        # header
        template = readTextFile("JS_htmlHeader.txt")
        header = template.format(params = self.params)
        buff.write(header)
        # write the code to set up experiment
        buff.setIndentLevel(4, relative=False)
        template = readTextFile("JS_setupExp.txt")
        code = template.format(params=self.params)
        buff.writeIndentedLines(code)

    def writeStartCode(self, buff):
        code = ("# Ensure that relative paths start from the same directory "
                "as this script\n"
                "_thisDir = os.path.dirname(os.path.abspath(__file__))."
                "decode(sys.getfilesystemencoding())\n"
                "os.chdir(_thisDir)\n\n"
                "# Store info about the experiment session\n")
        buff.writeIndentedLines(code)

        if self.params['expName'].val in [None, '']:
            buff.writeIndented("expName = 'untitled.py'\n")
        else:
            code = ("expName = %s  # from the Builder filename that created"
                    " this script\n")
            buff.writeIndented(code % self.params['expName'])
        expInfo = self.params['Experiment info'].val.strip()
        if not len(expInfo):
            expInfo = '{}'
        try:
            expInfoDict = eval('dict(' + expInfo + ')')
        except SyntaxError:
            logging.error('Builder Expt: syntax error in '
                          '"Experiment info" settings (expected a dict)')
            raise AttributeError('Builder: error in "Experiment info"'
                                 ' settings (expected a dict)')
        buff.writeIndented("expInfo = %s\n" % expInfo)
        if self.params['Show info dlg'].val:
            buff.writeIndentedLines(
                "dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)\n"
                "if dlg.OK == False:\n    core.quit()  # user pressed cancel\n")
        buff.writeIndentedLines(
            "expInfo['date'] = data.getDateStr()  # add a simple timestamp\n"
            "expInfo['expName'] = expName\n")
        level = self.params['logging level'].val.upper()

        saveToDir = self.getSaveDataDir()
        buff.writeIndentedLines("\n# Data file name stem = absolute path +"
                                " name; later add .psyexp, .csv, .log, etc\n")
        # deprecated code: before v1.80.00 we had 'Saved data folder' param
        # fairly fixed filename
        if 'Saved data folder' in self.params:
            participantField = ''
            for field in ('participant', 'Participant', 'Subject', 'Observer'):
                if field in expInfoDict:
                    participantField = field
                    self.params['Data filename'].val = (
                        repr(saveToDir) + " + os.sep + '%s_%s' % (expInfo['" +
                        field + "'], expInfo['date'])")
                    break
            if not participantField:
                # no participant-type field, so skip that part of filename
                self.params['Data filename'].val = repr(
                    saveToDir) + " + os.path.sep + expInfo['date']"
            # so that we don't overwrite users changes doing this again
            del self.params['Saved data folder']

        # now write that data file name to the script
        if not self.params['Data filename'].val:  # i.e., the user deleted it
            self.params['Data filename'].val = (
                repr(saveToDir) +
                " + os.sep + u'psychopy_data_' + data.getDateStr()")
        # detect if user wanted an absolute path -- else make absolute:
        filename = self.params['Data filename'].val.lstrip('"\'')
        # (filename.startswith('/') or filename[1] == ':'):
        if filename == os.path.abspath(filename):
            buff.writeIndented("filename = %s\n" %
                               self.params['Data filename'])
        else:
            buff.writeIndented("filename = _thisDir + os.sep + %s\n" %
                               self.params['Data filename'])

        # set up the ExperimentHandler
        code = ("\n# An ExperimentHandler isn't essential but helps with "
                "data saving\n"
                "thisExp = data.ExperimentHandler(name=expName, version='',\n"
                "    extraInfo=expInfo, runtimeInfo=None,\n"
                "    originPath=%s,\n")
        buff.writeIndentedLines(code % repr(self.exp.expPath))

        code = ("    savePickle=%(Save psydat file)s, saveWideText=%(Save "
                "wide csv file)s,\n    dataFileName=filename)\n")
        buff.writeIndentedLines(code % self.params)

        if self.params['Save log file'].val:
            code = ("# save a log file for detail verbose info\nlogFile = "
                    "logging.LogFile(filename+'.log', level=logging.%s)\n")
            buff.writeIndentedLines(code % level)
        buff.writeIndented("logging.console.setLevel(logging.WARNING)  "
                           "# this outputs to the screen, not a file\n")

        # >> ioHub Code written at start of experiment....
        # Create launchHubServer kwargs dict based on experiment settings...

        # Remaining TODO:
        #  If HDF5 saving is enabled:
        #  * For experiment info entries:
        #
        #          * [TODO] Field names matching exp_[field] would map to associated
        #            launchHubServer experiment_info dict[field] kwarg value
        #            when [field] is one of:
        #                 - title
        #                 - description
        #                 - version
        #
        #          * [TODO] Field names matching sess_[field] would map to associated launchHubServer
        #            session_info dict[field] kwarg value when [field] is one of:
        #                  - name
        #                  - comments
        #
        #         * [TODO] Any remaining experiment info fields would be added as key:value pairs to the
        #           optional session_info dict['user_variables'] entry.

        #  If requested, enable iohub for experiment
        use_iohub = self.params['useIoHub'].val
        if use_iohub:
            iohub_config_ = dict()
            save_hdf5_file = self.params['useHDF5'].val

            if self.params['ioHubConfigFile'].val:
                iohub_config_file = self.params['ioHubConfigFile'].val
                if os.path.isabs(iohub_config_file):
                    if os.path.exists(iohub_config_file):
                        iohub_config_['iohub_config_name'] = 'u"%s"' % iohub_config_file
                    else:
                        # TODO: Replace with proper way to show a buildtime error.
                        print("Builder ERROR: ioHub Config File Does not Exist:",iohub_config_file)
                else:
                    # Relative file path given, so assume that at runtime
                    # os.join(os.cwd(), iohub_config_name) is a valid file path
                    iohub_config_['iohub_config_name'] = 'u"%s"' % iohub_config_file

            # Display device related kwargs
            # TODO: Make screen index validation code in .writeWindowCode
            #       a reusable function and use it here too.
            screen_index_ = int(self.params['Screen'].val)
            coord_unit_type_ = self.params['Units'].val
            if coord_unit_type_ == 'use prefs':
                # TODO: Look into how to get actual unit type when 'use prefs'
                # for now, default to 'pix'
                coord_unit_type_ = 'pix'
            coord_unit_type_ = "'%s'"%coord_unit_type_
            iohub_config_['Display'] = dict(device_number=screen_index_,
                                            reporting_unit_type=coord_unit_type_)

            psycho_monitor_file_ = self.params['Monitor'].val
            if psycho_monitor_file_:
                #TODO: Check that file exists and give build error if not
                iohub_config_['psychopy_monitor_name'] = '"%s"'%psycho_monitor_file_

            if save_hdf5_file:
                # These kwargs are only added if the hdf5 file is being saved
                iohub_config_['experiment_info'] = experiment_info_ = dict()
                experiment_info_['code'] = 'expName'

                if u'session' in expInfoDict.keys():
                    iohub_config_['session_info'] = session_info_ = dict()
                    session_info_['code'] = "expInfo.get(u'session')"

                iohub_config_['datastore_name'] = u'filename'

            kwargs_str = u""
            for lkey, lval in iohub_config_.items():
                if isinstance(lval, dict):
                    sval = u""
                    for sk, sv, in lval.items():
                        sval += u"%s=%s, "%(sk, sv)
                    lval = u"dict(%s)"%sval[:-2]
                kwargs_str+=u"{}={},\n    ".format(lkey, lval)

            # Remove the ending ",\n    " 6 chars from code txt
            kwargs_str = kwargs_str[:-6]
            buff.writeIndentedLines(u"\n# >> Begin Launch ioHub Server Code\n"
                                   u"\n# start the ioHub Server\n"
                                   u"iohub_server = launchHubServer(%s)\n"
                                   u"\n# << End Launch ioHub Server Code\n"%kwargs_str)

        if self.exp.settings.params['Enable Escape'].val:
            buff.writeIndentedLines("\nendExpNow = False  # flag for 'escape'"
                                    " or other condition => quit the exp\n")

    def writeWindowCode(self, buff):
        """Setup the window code.
        """
        buff.writeIndentedLines("\n# Setup the Window\n")
        # get parameters for the Window
        fullScr = self.params['Full-screen window'].val
        # if fullscreen then hide the mouse, unless its requested explicitly
        allowGUI = (not bool(fullScr)) or bool(self.params['Show mouse'].val)
        allowStencil = False
        # NB routines is a dict:
        for thisRoutine in self.exp.routines.values():
            # a single routine is a list of components:
            for thisComp in thisRoutine:
                if thisComp.type == 'Aperture':
                    allowStencil = True
                if thisComp.type == 'RatingScale':
                    allowGUI = True  # to have a mouse

        requestedScreenNumber = int(self.params['Screen'].val)
        try:
            nScreens = wx.Display.GetCount()
        except Exception:
            # will fail if application hasn't been created (e.g. in test
            # environments)
            nScreens = 10
        if requestedScreenNumber > nScreens:
            logging.warn("Requested screen can't be found. Writing script "
                         "using first available screen.")
            screenNumber = 0
        else:
            # computer has 1 as first screen
            screenNumber = requestedScreenNumber - 1

        if fullScr:
            size = wx.Display(screenNumber).GetGeometry()[2:4]
        else:
            size = self.params['Window size (pixels)']
        code = ("win = visual.Window(\n    size=%s, fullscr=%s, screen=%s,"
                "\n    allowGUI=%s, allowStencil=%s,\n")
        vals = (size, fullScr, screenNumber, allowGUI, allowStencil)
        buff.writeIndented(code % vals)
        code = ("    monitor=%(Monitor)s, color=%(color)s, "
                "colorSpace=%(colorSpace)s,\n")
        if self.params['blendMode'].val:
            code += "    blendMode=%(blendMode)s, useFBO=True,\n"

        if self.params['Units'].val != 'use prefs':
            code += "    units=%(Units)s"
        code = code.rstrip(', \n') + ')\n'
        buff.writeIndentedLines(code % self.params)

        if 'microphone' in self.exp.psychopyLibs:  # need a pyo Server
            buff.writeIndentedLines("\n# Enable sound input/output:\n"
                                    "microphone.switchOn()\n")

        code = ("# store frame rate of monitor if we can measure it\n"
                "expInfo['frameRate'] = win.getActualFrameRate()\n"
                "if expInfo['frameRate'] != None:\n"
                "    frameDur = 1.0 / round(expInfo['frameRate'])\n"
                "else:\n"
                "    frameDur = 1.0 / 60.0  # could not measure, so guess\n")
        buff.writeIndentedLines(code)

    def writeWindowCodeJS(self, buff):
        template = readTextFile("JS_winInit.txt")
        code = template.format(params=self.params)
        buff.writeIndentedLines(code)

    def writeEndCode(self, buff):
        """Write code for end of experiment (e.g. close log file).
        """
        buff.writeIndented("# these shouldn't be strictly necessary "
                           "(should auto-save)\n")
        if self.params['Save wide csv file'].val:
            buff.writeIndented("thisExp.saveAsWideText(filename+'.csv')\n")
        if self.params['Save psydat file'].val:
            buff.writeIndented("thisExp.saveAsPickle(filename)\n")
        if self.params['Save log file'].val:
            buff.writeIndented("logging.flush()\n")
        code = ("# make sure everything is closed down\n"
                "thisExp.abort()  # or data files will save again on exit\n"
                "win.close()\n")
        if self.params['useIoHub'].val:
            code += 'iohub_server.quit()\n'
        code += "core.quit()\n"
        buff.writeIndentedLines(code)

    def writeEndCodeJS(self, buff):
        quitFunc = ("\nfunction quitPsychoJS() {\n"
                    "    win.close()\n"
                    "    core.quit();\n"
                    "    return QUIT;\n"
                    "}")
        footer = ("\n"
                  "        run();\n"
                  "        }\n"
                  "      });\n"
                  "    </script>\n\n"
                  "  </body>\n"
                  "</html>")
        buff.writeIndentedLines(quitFunc)
        buff.write(footer)
