import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCore
import fsearch

ApplicationWindow {
    id: root
    color: 'silver'
    title: "Quick File Search"
    visible: true

    Component.onCompleted: {
        previewArea.visible = settings.previewVisable;

        if (previewArea.visible) {
            root.width = settings.winWidthPreview;
            searchArea.width = settings.searchWidthPreview;
        } else {
            root.width = settings.windowWidth;
        }
        height = settings.windowHeight;
        Utils.mainText = settings.sizing;
        filelist.filenameWidth = settings.fileNameWidth;
        x = settings.x;
        y = settings.y;
        search_input.focus = true;
        // Backend.startScanSignal();
        scan_timer.start();
        Backend.requestFavoritesSignal();
    }

    Component.onDestruction: {
        // Save current window size
        settings.previewVisable = previewArea.visible;
        if (previewArea.visible) {
            settings.winWidthPreview = root.width;
            settings.searchWidthPreview = searchArea.width;
        } else {
            settings.windowWidth = root.width;
        }
        settings.windowHeight = height;
        settings.sizing = Utils.mainText;
        settings.x = x;
        settings.y = y;
    }

    Timer {
        id: scan_timer
        interval: 1.8e+6
        // interval:60000
        repeat: true
        triggeredOnStart: true
        onTriggered: Backend.startScanSignal()
    }

    onClosing: {
        Backend.shutdown();  // Call the shutdown method
    }

    function change_selection(chng) {
        if (!filelist.model)
            return; // Safety check

        if (chng < 0) {
            filelist.selected = Math.max(filelist.selected + chng, 0);
        } else {
            let maxIdx = filelist.model.rowCount() - 1;
            // console.log(chng)
            filelist.selected = Math.min(filelist.selected + chng, maxIdx);
        }

        filelist.positionViewAtIndex(filelist.selected, ListView.Center);
    }

    //MARK: settings
    Settings {
        id: settings

        property int sizing: 20
        property int windowHeight: 600
        property int windowWidth: 800
        property int winWidthPreview: 1800
        property int searchWidthPreview: 800
        property int fileNameWidth: 12
        property bool previewVisable: false
        property int x: 100
        property int y: 100
    }

    Item {
        id: focusOverlay
        anchors.fill: parent     // cover the entire window
        z: 10                    // stay on top

        /** track current focus target */
        property Item target: root.activeFocusItem

        /* keep geometry in sync */
        onTargetChanged: updateGeometry()
        Component.onCompleted: updateGeometry()

        function updateGeometry() {
            if (!target) {
                rect.visible = false;
                return;
            }
            rect.visible = true;
            const p = target.mapToItem(focusOverlay, 0, 0);
            rect.x = p.x + target.width - 8;
            rect.y = p.y;
        // rect.width  = target.width  + 4
        // rect.height = target.height + 4
        }

        Rectangle {
            id: rect
            visible: false
            color: "tomato"
            // border.color: "orange"
            // border.width: 4
            radius: 4
            width: 8
            height: 8
        }
    }

    SplitView {
        id: mainSplitView

        anchors.fill: parent
        orientation: Qt.Horizontal

        Rectangle {
            id: searchArea
            SplitView.minimumWidth: 300
            SplitView.preferredWidth: settings.windowWidth
            // SplitView.maximumWidth: 400
            color: 'lightgray'
            Loader {
                id: screenLoader
                anchors.fill: parent
                z: 1000
            }
            Item {
                id: searchContainer
                anchors.fill: parent
                Rectangle {
                    id: search_input_rect

                    x: 10
                    y: 10
                    anchors.topMargin: 10
                    border.color: 'gray'
                    border.width: 2
                    color: 'white'
                    height: search_input.implicitHeight + 5
                    radius: 5
                    width: parent.width - 400

                    Text {
                        id: search_input_placeholder

                        anchors.left: parent.left
                        anchors.leftMargin: 7
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        color: 'gray'
                        font.pixelSize: Utils.mainText
                        text: search_input.text == "" ? "Search..." : ""
                    }
                    //MARK:search
                    TextInput {
                        id: search_input
                        KeyNavigation.tab: search_input
                        anchors.left: parent.left
                        anchors.leftMargin: 7
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        color: 'black'
                        font.pixelSize: Utils.mainText

                        onTextChanged: {
                            searchDebounceTimer.restart();
                        }
                    }
                    Timer {
                        id: searchDebounceTimer

                        interval: 200
                        repeat: false

                        onTriggered: Backend.searchFiles(search_input.text)
                    }
                }
                Rectangle {
                    id: file_list_rect

                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 10
                    // height:200
                    anchors.left: search_input_rect.left
                    anchors.top: search_input_rect.bottom
                    anchors.topMargin: 10
                    border.color: 'gray'
                    border.width: 2
                    radius: 5
                    width: parent.width - 20

                    FileList {
                        id: filelist

                        focus: false
                        selected: 0
                    }
                }
                Text {
                    id: nav_text

                    text: `F1 Help, F2 Folders, F3 Ignore, F4 Scan, F5 File Rev`
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    anchors.top: parent.top
                    anchors.topMargin: 10
                }
                Text {
                    id: status_text

                    anchors.left: search_input_rect.right
                    anchors.leftMargin: 10
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    anchors.top: nav_text.bottom
                    anchors.topMargin: 0
                    clip: true
                    color: 'darkred'
                    font.pixelSize: Utils.mainText - 6
                    horizontalAlignment: Text.AlignRight
                    text: Backend.scanStatus
                    wrapMode: Text.Wrap
                }
            }
        }

        //MARK:previewArea
        Rectangle {
            id: previewArea
            SplitView.minimumWidth: 300
            SplitView.preferredWidth: 600
            color: 'lightgray'
            visible: false

            Viewer {
                id: viewerManager
                sizing: Utils.mainText
            }
        }
    }

    function toggle_view2(qml_file) {
        if (screenLoader.source == qml_file) {
            screenLoader.source = "";
            search_input.focus = true;
            // search_input_rect.visible = true;
            // search_input_rect.visible = true;
            searchContainer.visible = true;
        } else {
            screenLoader.source = qml_file;
            searchContainer.visible = false;
            // search_input_rect.visible = false;
            // file_list_rect.visible = false;
        }
    }

    function togglePreview() {
        if (previewArea.visible) {
            settings.winWidthPreview = root.width;
            settings.searchWidthPreview = searchArea.width;
            search_input.focus = true;
        } else {
            settings.windowWidth = root.width;
        }

        previewArea.visible = !previewArea.visible;
        if (previewArea.visible) {
            root.width = settings.winWidthPreview;
            searchArea.width = settings.searchWidthPreview;
        } else {
            root.width = settings.windowWidth;
        }
    }

    //    MARK:F1
    Shortcut {
        sequences: ['F1']
        onActivated: root.toggle_view2("HelpScreen.qml")
    }
    Shortcut {
        sequences: ['F2']
        onActivated: root.toggle_view2("ManageTables.qml")
    }
    Shortcut {
        sequences: ['F3']
        onActivated: root.toggle_view2("ManageIgnore.qml")
    }
    Shortcut {
        sequences: ['F4']
        onActivated: scan_timer.restart()
    }
    Shortcut {
        sequences: ['F5']
        onActivated: root.toggle_view2("ManageSharepointPaths.qml")
    }
    Shortcut {
        sequences: ['Ctrl+e']
        onActivated: {
            var fullPath = filelist.get_full_path();
            if (fullPath != "") {
                FileOps.revealInExplorer(fullPath);
            }
        }
    }
    Shortcut {
        enabled: searchContainer.visible
        sequences: ['Enter', 'Return']
        onActivated: {
            var fullPath = filelist.get_full_path();
            if (fullPath != "") {
                FileOps.openFile(fullPath);
            }
        }
    }
    Shortcut {
        sequences: ['Ctrl+Shift+c']
        enabled: searchContainer.visible
        onActivated: {
            var fullPath = filelist.get_full_path();
            if (fullPath != "") {
                FileOps.copy(fullPath);
            }
        }
    }
    Shortcut {
        sequences: ['Shift+Enter', 'Shift+Return']
        enabled: searchContainer.visible
        onActivated: {
            if (!previewArea.visible) {
                root.togglePreview();
            }
            var fullPath = filelist.get_full_path();
            if (fullPath != "") {
                viewerManager.openFileInViewer(fullPath);
            }
        }
    }
    //MARK:prevw_Shortcut
    Shortcut {
        sequences: ['Ctrl+p']
        // context: Qt.ApplicationShortcut
        onActivated: root.togglePreview()
    }

    Shortcut {
        sequences: ['Escape']
        onActivated: {
            screenLoader.source = "";
            search_input.text = "";
            Backend.requestFavoritesSignal();
            search_input.focus = true;
            searchContainer.visible = true;
        }
    }
    Shortcut {
        sequences: ['Ctrl+=']
        onActivated: Utils.mainText += 1
    }
    Shortcut {
        sequences: ['Ctrl+-']
        onActivated: Utils.mainText -= 1
    }
    Shortcut {
        sequences: ['Down']
        enabled: searchContainer.visible
        onActivated: root.change_selection(1)
    }
    Shortcut {
        sequences: ['Up']
        enabled: searchContainer.visible
        onActivated: root.change_selection(-1)
    }
    Shortcut {
        sequences: ['Ctrl+Shift+.']
        enabled: searchContainer.visible
        onActivated: {
            filelist.filenameWidth += 1;
            settings.fileNameWidth = filelist.filenameWidth;
        }
    }
    Shortcut {
        sequences: ['Ctrl+Shift+,']
        enabled: searchContainer.visible
        onActivated: {
            filelist.filenameWidth -= 1;
            settings.fileNameWidth = filelist.filenameWidth;
        }
    }
    Shortcut {
        sequences: ['Ctrl+q']
        context: Qt.ApplicationShortcut
        onActivated: Qt.quit()
    }
    Shortcut {
        sequences: ['Ctrl+Up']
        onActivated: {
            enabled: searchContainer.visible;
            filelist.selected = 0;
            filelist.scroll_zero();
            root.change_selection(-1);
        }
    }
    Shortcut {
        sequences: ['Ctrl+Down']
        onActivated: {
            enabled: searchContainer.visible;
            filelist.selected = filelist.count - 1;
            filelist.positionViewAtIndex(filelist.selected, ListView.End);
        }
    }
    Shortcut {
        sequences: ['Ctrl+d']
        enabled: searchContainer.visible
        onActivated: {
            if (filelist.model && filelist.model.rowCount() > 0 && filelist.selected >= 0 && filelist.selected < filelist.model.rowCount()) {
                var fullPath = filelist.get_full_path();
                var fileName = filelist.model.data(filelist.model.index(filelist.selected, 0), filelist.model.FilenameRole);
                console.log("Adding favorite for:", fullPath);
                filelist.itemAtIndex(filelist.selected).favorite = true
                // Backend.addFavoriteSignal(fullPath);
                AsyncRequest.insertRecord('favorites',['file_path'],[fullPath])
            }
        }
    }
    Shortcut {
        sequences: ['Ctrl+r']
        enabled: searchContainer.visible
        onActivated: {
            if (filelist.model && filelist.model.rowCount() > 0 && filelist.selected >= 0 && filelist.selected < filelist.model.rowCount()) {
                var fullPath = filelist.get_full_path();
                console.log("Removing favorite for:", fullPath);
                filelist.itemAtIndex(filelist.selected).favorite = false
                // Backend.removeFavoriteSignal(fullPath);
                AsyncRequest.deleteRecord('favorites','file_path',fullPath)
                // Backend.requestFavoritesSignal();
            }
        }
    }
    Shortcut {
        sequences: ['PgDown']
        enabled: searchContainer.visible
        onActivated: {
            var c = filelist.getVisibleRowCount();
            root.change_selection(c);
        }
    }
    Shortcut {
        sequences: ['PgUp']
        enabled: searchContainer.visible
        onActivated: {
            var c = filelist.getVisibleRowCount();
            root.change_selection(-c);
        }
    }
}
