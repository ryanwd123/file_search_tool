import QtQuick
import QtQuick.Pdf
import QtQuick.Window

Window {
    id:root
    height: 800
    width: 1200
    x: 100
    y: 100
    visible: true
    title: "PDF Reader"
    
    Rectangle{
        anchors.fill:parent
        onWidthChanged: scale_to_width()

        // Top bar with page indicators
        Rectangle {
            id: topBar
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 30
            color: "#f0f0f0"
            border.color: "#d0d0d0"
            border.width: 1
            z: 1

            Text {
                id: pageIndicator
                anchors.centerIn: parent
                text: "Page " + (pdf.currentPage + 1) + " of " + pdf.document.pageCount
                font.pixelSize: 14
                font.family: "Arial"
                color: "#333333"
            }
            Text {
                anchors.right:search_rect.left
                anchors.verticalCenter:search_rect.verticalCenter
                text:'Search (Enter/Shift+Enter)  '
                font.pixelSize:14
            }


            Rectangle{
                id:search_rect
                anchors.right:parent.right
                anchors.verticalCenter:parent.verticalCenter
                height:search.implicitHeight
                width:200
                color:'white'
                TextInput{
                    id:search
                    anchors.fill:parent
                    font.pixelSize:20

                    // onAccepted: {
                    // if (pdf.searchString != search.text) {
                    //      pdf.searchString = search.text
                    //     }
                    //     pdf.searchForward()
                    // }

                    Shortcut{
                        sequences: ['Return']
                        onActivated: {
                        if (pdf.searchString != search.text) {
                            pdf.searchString = search.text
                            }
                            pdf.searchForward()
                        }
                    }
                    Shortcut{
                        sequences: ['Shift+Return']
                        onActivated: {
                        if (pdf.searchString != search.text) {
                            pdf.searchString = search.text
                            }
                            pdf.searchBack()
                        }
                    }


                }
            }

        }

        PdfMultiPageView {
            id:pdf
            anchors.top: topBar.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            document: PdfDocument { source: defaultPdfPath }
            

        }


    function scale_to_width (params) {
            // Calculate scale to fit width
            if (pdf.document.status === PdfDocument.Ready && pdf.document.pageCount > 0) {
                var pageSize = pdf.document.pagePointSize(0)
                var scale = (root.width / pageSize.width)-.02
                console.log(scale)
                pdf.renderScale = scale
            }
        }
    }
}