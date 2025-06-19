import QtQuick
import QtQuick.Controls


    Item {
    id:root1
    anchors.centerIn:parent
    width:parent.width-10
    height:parent.height-10
    z:1000
        Rectangle{
            anchors.fill: parent
            radius:5
            border.color:'black'
            border.width:5
            color:'tomato'
        
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            // This MouseArea will consume all mouse events when visible
            // preventing them from reaching underlying elements
        }

        Text {
            id: closeInstructions
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.topMargin: 10
            anchors.rightMargin: 15
            text: "F1 to close"
            font.pixelSize: Utils.mainText - 4
            font.family: "consolas"
            color: 'darkred'
        }


        Text{
            id:title
            anchors.top:parent.top
            anchors.topMargin:10
            anchors.horizontalCenter:parent.horizontalCenter
            text:"Help Screen"
            font.pixelSize:Utils.mainText + 20
            font.family:"consolas"
        }
        
        // White rectangle background for help text
        Rectangle {
            id: whiteBackground
            anchors.top: title.bottom
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.leftMargin: 20
            anchors.rightMargin: 20
            anchors.topMargin: 10
            anchors.bottomMargin: 20
            
            color: "white"
            border.color: "black"
            border.width: 2
            radius: 5
        }
        
        ScrollView {
            anchors.top:title.bottom
            anchors.left:parent.left
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.leftMargin:30
            anchors.rightMargin:30
            anchors.topMargin:20
            anchors.bottomMargin:30

        Text{
            id:help_text
            anchors.top:parent.top
            anchors.left:parent.left
            text:`
Settings/Help
    Toggle Help Screen:         F1
    Folders to index:           F2
    Folders to ignore:          F3
    Quit application:           Ctrl+Q
    Clear Search:               Escape
    Toggle Preview:             Ctrl+P

    Increase size/zoom:         Ctrl+=
    Decrease size/zoom:         Ctrl+-

    Increase Filename Width     Ctrl+Shift+.
    Decrease Filename Width     Ctrl+Shift+,

File List Navigation
    Move selection up:          Up Arrow
    Move selection down:        Down Arrow
    Go to first item:           Ctrl+Up
    Go to last item:            Ctrl+Down
`
            font.pixelSize:Utils.mainText
            font.family:'consolas'
        }
        }
        }
    }