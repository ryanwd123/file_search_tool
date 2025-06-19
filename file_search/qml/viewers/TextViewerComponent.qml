import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtCore
import fsearch


Rectangle {
    id: root
    
    property string filePath: ""
    focus:false

    
    // onFilePathChanged: {
    //     if (filePath !== "") {
    //         fileContent = FileOps.readText(filePath)
    //         textArea.text = fileContent
    //     }
    // }

    color: "#ffffff"
    
    // File content loader
    property string fileContent: ""
    
    Settings{
        id:settings
        property int textsize: 14
    }

    

    
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Top toolbar
        Rectangle {
            id: toolbar
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: "#f0f0f0"
            border.color: "#d0d0d0"
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 10
                
                Text {
                    text: "File: " + (root.filePath.split(/[/\\]/).pop() || "")
                    font.pixelSize: settings.textsize
                    color: "#333333"
                }
                
                Item { Layout.fillWidth: true } // Spacer
                Button {
                    text: "+"
                    Layout.preferredWidth: 30
                    Layout.preferredHeight: 24
                    onClicked: root.increaseFont()
                }
                Button {
                    text: "-"
                    Layout.preferredWidth: 30
                    Layout.preferredHeight: 24
                    onClicked: root.decreaseFont()
                }
                
                

            }
        }
        
        // Text content area
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            focus:false

            
            TextArea {
                id: textArea
                textFormat: Text.RichText
                wrapMode: TextArea.Wrap
                readOnly:true
                focus:false
                font.family: "Consolas, Monaco, monospace"
                font.pixelSize: settings.textsize
                color: "black"
                text: FileOps.readText(root.filePath)
                
                // Line numbers (optional enhancement)
                property int lineCount: text.split('\n').length
            }
        }
        

    }
    

    


    function increaseFont() {
        textArea.font.pixelSize+=1
        settings.textsize = textArea.font.pixelSize
        
    }
    function decreaseFont() {
        textArea.font.pixelSize-=1
        settings.textsize = textArea.font.pixelSize
    }
    
    // Keyboard shortcuts

    

}