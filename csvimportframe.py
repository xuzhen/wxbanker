import wx
from csvimporter import CsvImporter, CsvImporterProfileManager, json
from transactionolv import TransactionOLV as TransactionCtrl

class CsvImportFrame(wx.Frame):
    """
    Window for importing data from a CSV file
    """
    def __init__(self, bankController):
        wx.Frame.__init__(self, None, title=_("CSV import"))
        
        self.bankModel = bankController.Model
        
        self.dateFormats = ['%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']
        self.encodings = ['cp1250', 'utf-8']
        self.profileManager = CsvImporterProfileManager()
        
        topPanel = wx.Panel(self)
        topHorizontalSizer = wx.BoxSizer(wx.VERTICAL)
        topSizer = wx.BoxSizer(wx.VERTICAL)

        horizontalSizer = wx.BoxSizer(wx.HORIZONTAL)
        topSizer.Add(horizontalSizer)
        self.initSettingsControls(topPanel, horizontalSizer)
        self.initSettingsProfilesControl(topPanel, horizontalSizer)
        
        self.initFileAndActionControls(topPanel, topSizer)
        self.initTransactionCtrl(topPanel, topSizer)
        
        self.initTargetAccountControl(topPanel, topSizer)
        
        # set default values
        self.initCtrlValuesFromSettings(self.getDefaultSettings())
        
        # layout sizers
        topPanel.SetSizer(topSizer)
        topPanel.SetAutoLayout(True)
        topSizer.Fit(self)
        
        self.Show(True)
        
    def initTargetAccountControl(self, topPanel, topSizer):
        staticBox = wx.StaticBox(topPanel, label=_("Target account"))
        staticBoxSizer = wx.StaticBoxSizer(staticBox, wx.HORIZONTAL)
        topSizer.Add(staticBoxSizer, flag=wx.ALL|wx.EXPAND, border=1)

        try:
            accounts = [acc.GetName() for acc in self.bankModel.Accounts]
        except:
            accounts = []
        
        self.targetAccountCtrl = wx.ComboBox(topPanel, style=wx.CB_READONLY, choices=accounts)
        self.targetAccountCtrl.Bind(wx.EVT_COMBOBOX, self.onTargetAccountChange)
        staticBoxSizer.Add(self.targetAccountCtrl)
        
        self.importButton = wx.Button(topPanel, label=_("Import"))
        self.importButton.Disable()
        self.importButton.SetToolTipString(_("Import"))
        self.importButton.Bind(wx.EVT_BUTTON, self.onClickImportButton)
        staticBoxSizer.Add(self.importButton, flag=wx.LEFT, border=5)
        
    def initSettingsControls(self, topPanel, parentSizer):
        # csv columns to wxBanker data mapping
        
        topSizer = wx.BoxSizer(wx.VERTICAL)
        parentSizer.Add(topSizer)
        
        staticBox = wx.StaticBox(topPanel, label=_("CSV columns mapping"))
        staticBoxSizer = wx.StaticBoxSizer(staticBox, wx.VERTICAL)
        topSizer.Add(staticBoxSizer, flag=wx.ALL|wx.EXPAND, border=1)
        
        sizer = wx.FlexGridSizer(rows=3, cols=4, hgap=15, vgap=0)
        sizer.SetFlexibleDirection(wx.HORIZONTAL)
        staticBoxSizer.Add(sizer, flag=wx.ALL|wx.EXPAND, border=5)
        
        self.dateColumnCtrl = wx.SpinCtrl(topPanel, size=(40,-1))
        sizer.Add(wx.StaticText(topPanel, label=_('Date')), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.dateColumnCtrl, flag=wx.ALIGN_CENTER_VERTICAL)
        self.dateFormatCtrl = wx.ComboBox(topPanel, choices=self.dateFormats, size=(110,-1))
        sizer.Add(wx.StaticText(topPanel, label=_('Date format')), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.dateFormatCtrl, flag=wx.ALIGN_CENTER_VERTICAL)
        
        self.amountColumnCtrl = wx.SpinCtrl(topPanel, size=(40,-1))
        self.decimalSeparatorCtrl = wx.TextCtrl(topPanel, size=(20,-1))
        sizer.Add(wx.StaticText(topPanel, label=_('Amount')), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.amountColumnCtrl, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticText(topPanel, label=_('Decimal separator')), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.decimalSeparatorCtrl, flag=wx.ALIGN_CENTER_VERTICAL)
        
        self.descriptionColumnCtrl = wx.TextCtrl(topPanel)
        sizer.Add(wx.StaticText(topPanel, label=_('Description')), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.descriptionColumnCtrl, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add((0,0))
        sizer.Add((0,0))
        
        # csv file settings - delimiter, encoding, first line has headers - skipped
        
        staticBox = wx.StaticBox(topPanel, label=_("CSV file settings"))
        staticBoxSizer = wx.StaticBoxSizer(staticBox, wx.VERTICAL)
        topSizer.Add(staticBoxSizer, flag=wx.ALL|wx.EXPAND, border=1)
        
        sizer = wx.FlexGridSizer(rows=3, cols=2, hgap=15, vgap=0)
        sizer.SetFlexibleDirection(wx.HORIZONTAL)
        staticBoxSizer.Add(sizer);
        
        self.skipFirstLineCtrl = wx.CheckBox(topPanel)
        sizer.Add(wx.StaticText(topPanel, label=_('Skip first line')), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.skipFirstLineCtrl, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(wx.StaticText(topPanel, label=_('Encoding')), flag=wx.ALIGN_CENTER_VERTICAL)
        self.fileEncodingCtrl = wx.ComboBox(topPanel, choices=self.encodings, size=(110,-1))
        sizer.Add(self.fileEncodingCtrl, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(wx.StaticText(topPanel, label=_('Column delimiter')), flag=wx.ALIGN_CENTER_VERTICAL)
        self.delimiterCtrl = wx.TextCtrl(topPanel, size=(30,-1))
        self.delimiterCtrl.SetMaxLength(1)
        sizer.Add(self.delimiterCtrl, flag=wx.ALIGN_CENTER_VERTICAL)
        
    def initFileAndActionControls(self, topPanel, topSizer):
        # file picker control and import button
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        topSizer.Add(sizer, flag=wx.EXPAND|wx.ALL, border=5)
        
        sizer.Add(wx.StaticText(topPanel, label=_('File to import')), flag=wx.ALIGN_CENTER_VERTICAL)
        self.filePickerCtrl = wx.FilePickerCtrl(topPanel)
        self.filePickerCtrl.Bind(wx.EVT_FILEPICKER_CHANGED, self.onFileChange)
        sizer.Add(self.filePickerCtrl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, proportion=2, border=10)
        
        self.previewButton = wx.Button(topPanel, label=_("Preview"))
        self.previewButton.Disable()
        self.previewButton.SetToolTipString(_("Prevoew"))
        self.previewButton.Bind(wx.EVT_BUTTON, self.onClickPreviewButton)
        sizer.Add(self.previewButton)
        
    def initTransactionCtrl(self, topPanel, topSizer):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        topSizer.Add(sizer, flag=wx.EXPAND|wx.ALL, proportion=1, border=5)
        
        self.transactionCtrl = TransactionCtrl(topPanel, None)
        sizer.Add(self.transactionCtrl, flag=wx.ALL|wx.EXPAND, proportion=1)
        
    def initSettingsProfilesControl(self, topPanel, topSizer):
        staticBox = wx.StaticBox(topPanel, label=_("CSV profiles"))
        sizer = wx.StaticBoxSizer(staticBox, wx.VERTICAL)
        topSizer.Add(sizer, flag=wx.ALL|wx.EXPAND)

        if not json:
            info = wx.StaticText(topPanel, label=_('Python simplejson library is needed for csv profile loading/saving.'),
                style=wx.ALIGN_CENTER)
            info.Wrap(80)
            sizer.Add(info, flag=wx.ALIGN_CENTER_VERTICAL)
            return
        
        self.profileCtrl = wx.ComboBox(topPanel, choices=self.profileManager.profiles.keys(), size=(110,-1))
        self.profileCtrl.Bind(wx.EVT_TEXT, self.onProfileCtrlChange)
        sizer.Add(self.profileCtrl, flag=wx.ALIGN_CENTER)
        
        self.loadProfileButton = wx.Button(topPanel, label=_("Load"))
        self.loadProfileButton.Bind(wx.EVT_BUTTON, self.onClickLoadProfileButton)
        self.loadProfileButton.Disable()
        sizer.Add(self.loadProfileButton, flag=wx.ALIGN_CENTER)
        
        self.saveProfileButton = wx.Button(topPanel, label=_("Save"))
        self.saveProfileButton.Bind(wx.EVT_BUTTON, self.onClickSaveProfileButton)
        self.saveProfileButton.Disable()
        sizer.Add(self.saveProfileButton, flag=wx.ALIGN_CENTER)
        
        self.deleteProfileButton = wx.Button(topPanel, label=_("Delete"))
        self.deleteProfileButton.Bind(wx.EVT_BUTTON, self.onClickDeleteProfileButton)
        self.deleteProfileButton.Disable()
        sizer.Add(self.deleteProfileButton, flag=wx.ALIGN_CENTER)
        
    def initCtrlValuesFromSettings(self, settings):
        self.amountColumnCtrl.Value = settings['amountColumn']
        self.decimalSeparatorCtrl.Value = settings['decimalSeparator']
        self.dateColumnCtrl.Value = settings['dateColumn']
        self.dateFormatCtrl.Value = settings['dateFormat']
        self.descriptionColumnCtrl.Value = settings['descriptionColumns']
        self.delimiterCtrl.Value = settings['delimiter']
        self.skipFirstLineCtrl.Value = settings['skipFirstLine']
        self.fileEncodingCtrl.Value = settings['encoding']
        
    def getDefaultSettings(self):
        settings = {}

        settings['amountColumn'] = 2
        settings['decimalSeparator'] = '.'
        settings['dateColumn'] = 1
        settings['dateFormat'] = self.dateFormats[0]
        settings['descriptionColumns'] = "3, 4 (5)"
        settings['delimiter'] = ';'
        settings['skipFirstLine'] = False
        settings['encoding'] = 'utf-8'
        
        return settings

    def getSettingsFromControls(self):
        settings = {}

        settings['amountColumn'] = self.amountColumnCtrl.Value
        settings['decimalSeparator'] = self.decimalSeparatorCtrl.Value
        settings['dateColumn'] = self.dateColumnCtrl.Value
        settings['dateFormat'] = self.dateFormatCtrl.Value
        settings['descriptionColumns'] = self.descriptionColumnCtrl.Value
        # delimiter must be 1-character string
        settings['delimiter'] = str(self.delimiterCtrl.Value)
        settings['skipFirstLine'] = self.skipFirstLineCtrl.Value
        settings['encoding'] = self.fileEncodingCtrl.Value
        
        return settings

    def runPreview(self):
        importer = CsvImporter()
        settings = self.getSettingsFromControls()
        
        file = self.filePickerCtrl.Path
        account = self.targetAccountCtrl.Value
        
        try:
            transactions = importer.getTransactionsFromFile(account, file, settings)
            self.transactionCtrl.SetObjects(transactions)
        except Exception, e:
            print 'Caught exception:', e
            
    def importTransactions(self):
        pass
        
    def onFileChange(self, event):
        if self.filePickerCtrl.Path != '':
            self.previewButton.Enable()
            
    def onTargetAccountChange(self, event):
        if self.filePickerCtrl.Path != '':
            self.importButton.Enable()
            
    def onProfileCtrlChange(self, event):
        if self.profileCtrl.Value != '':
            self.saveProfileButton.Enable()
            enabled = self.profileManager.getProfile(self.profileCtrl.Value) != None
            self.loadProfileButton.Enable(enabled)
            self.deleteProfileButton.Enable(enabled)
        else :
            self.loadProfileButton.Disable()
            self.saveProfileButton.Disable()
            self.deleteProfileButton.Disable()

    def onClickPreviewButton(self, event):
        self.runPreview()
        
    def onClickImportButton(self, event):
        self.importTransactions()

    def initProfileCtrl(self):
        self.profileCtrl.Items = self.profileManager.profiles.keys()
        self.onProfileCtrlChange(None)

    def onClickLoadProfileButton(self, event):
        key = self.profileCtrl.Value
        self.initCtrlValuesFromSettings(self.profileManager.getProfile(key))
        self.initProfileCtrl()

    def onClickSaveProfileButton(self, event):
        key = self.profileCtrl.Value
        self.profileManager.saveProfile(key, self.getSettingsFromControls())
        self.initProfileCtrl()

    def onClickDeleteProfileButton(self, event):
        key = self.profileCtrl.Value
        self.profileManager.deleteProfile(key)
        self.initProfileCtrl()

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = CsvImportFrame()
    app.MainLoop()
