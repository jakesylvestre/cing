package cing.client;

import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormSubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormSubmitEvent;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.gwtsolutions.components.client.ui.Message;

public class FormHandlerFile extends FormHandlerMain {

	private Button nextButton = null;
	private FileUpload fileUpload = null;
	private Message statusMessage = null;
	private Button submitButton = null;
	private Label labelFileUploadDone = null;
	private ListBox listBox_Program = null;
	private ListBox listBox_Type = null;
	private ListBox listBox_Subtype = null;
	private ListBox listBox_Other = null;
	@SuppressWarnings("unused")
    private HTML egHtml = null;

	public FormHandlerFile(iCing icing) {
		super(icing);
	}

	// When the submit starts, make sure the user selected a file to upload
	public void onSubmit(FormSubmitEvent event) {
		super.onSubmit(event);
		GenClient.showDebug("Starting submit from FormHandlerFile.");

        String fn = fileUpload.getFilename();

        GenClient.showDebug("Using fileName in FormHandlerFile: [" + fn + "]");
        /** Extra checks here for this class */
		if (fileUpload.getFilename().length() == 0) {
			Window.alert(c.ERROR()+"\n\n"+c.You_must_sele());
			event.setCancelled(true);
			return;
		}

		
		String fnNoPath = Utils.getFileNameWithoutPath(fn);
        GenClient.showDebug("Using fileNameWithoutPath in FormHandlerFile: [" + fnNoPath + "]");

		/** Keep block together */
        String program = Utils.getListBoxItemText( listBox_Program );
        String type = Utils.getListBoxItemText( listBox_Type );
        @SuppressWarnings("unused")
        String subType = Utils.getListBoxItemText( listBox_Subtype );
        @SuppressWarnings("unused")
        String other = Utils.getListBoxItemText( listBox_Other );
		
        if ( program.equals(Settings.FILE_PROGRAM_CING) &&
                type.equals(Settings.FILE_TYPE_VALIDATION_SETTINGS) ) {
            if ( ! fnNoPath.equals(Settings.VAL_SETS_CFG_DEFAULT_FILENAME)) {
                Window.alert(c.ERROR()+"\n\n"+c.Validation_setti() + Settings.VAL_SETS_CFG_DEFAULT_FILENAME);
                event.setCancelled(true);
                return;
            }
        }

        if ( program.equals(Settings.FILE_PROGRAM_CCPN) &&
                type.equals(Settings.FILE_TYPE_PROJECT) ) {
            if ( ! (fnNoPath.endsWith(".tgz") || fnNoPath.endsWith(".tar.gz"))) {
                Window.alert(c.ERROR()+"\n\n"+c.Please_end_filen() + " .tar.gz | .tgz");
                event.setCancelled(true);
                return;
            }
        }

        submitButton.setVisible(false);
        fileUpload.setVisible(false);
        
		labelFileUploadDone.setText(c.Uploading() +" " + fnNoPath);
		labelFileUploadDone.setVisible(true);
	}

	public void onSubmitComplete(FormSubmitCompleteEvent event) {
		super.onSubmitComplete(event);
		GenClient.showDebug("Now in FormHandlerFile.onSubmitComplete");

		statusMessage.removeStyleName("successBorder");
		statusMessage.removeStyleName("failureBorder");
		statusMessage.setVisible(true);
		if (exitCode.equals(Settings.RESPONSE_EXIT_CODE_SUCCESS)) {
			showUploadMessage(result);
			// Try to get the project name from it if not set already.
			icing.cingLogView.getProjectName();
		} else {
		    if ( result == null ) {
		        result = "Failed to get a result string from parent: FormHandlerMain#onSubmitComplete()";
		    }
			showUploadError(result);
		}
//        icing.cingLogView.getProjectName(); // try after each file upload. But commented out here because only 
//		expected to have a chance of success when the results was a success.
        GenClient.showDebug("Exiting FormHandlerFile.onSubmitComplete");		
	}

	private void showUploadError(String result) {
		statusMessage.addStyleName("failureBorder");
		// Swap between these two widgets.
		labelFileUploadDone.setVisible(false);
		fileUpload.setVisible(true);
		statusMessage.setText(result);
	}

	private void showUploadMessage(String result) {
		statusMessage.addStyleName("successBorder");
		String fn = fileUpload.getFilename();
		String type = Utils.getHTMLformTypeFromFileName(fn);
		String fnNoPath = Utils.getFileNameWithoutPath(fn);
		String labelTxt = fnNoPath + " (" + type + ") " + result;
		statusMessage.setText(labelTxt + " "+ c.uploaded() +".");
		labelFileUploadDone.setText(labelTxt);
		nextButton.setEnabled(true);
		RunView.submitButton.setEnabled(true);
	}

	public void setFileUpload(FileUpload fileUpload) {
		this.fileUpload = fileUpload;
	}

	public void setStatusMessage(Message statusMessage) {
		this.statusMessage = statusMessage;
	}

	public void setSubmitButton(Button submitButton) {
		this.submitButton = submitButton;
	}

	public void setLabelFileUploadDone(Label labelFileUploadDone) {
		this.labelFileUploadDone = labelFileUploadDone;
	}

	public void setNextButton(Button nextButton) {
		this.nextButton = nextButton;
	}

    public void setListBox_Program(ListBox listBox_Program) {
        this.listBox_Program = listBox_Program;
    }


    public void setListBox_Type(ListBox listBox_Type) {
        this.listBox_Type = listBox_Type;
    }


    public void setListBox_Subtype(ListBox listBox_Subtype) {
        this.listBox_Subtype = listBox_Subtype;
    }


    public void setListBox_Other(ListBox listBox_Other) {
        this.listBox_Other = listBox_Other;
    }


    public void setEgHtml(HTML egHtml) {
        this.egHtml = egHtml;
    }

}
