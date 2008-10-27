package cing.client;

import com.google.gwt.user.client.Random;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ChangeListener;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PushButton;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class Options extends iCingView {

//	static final private Random r = new Random();
	private Label accessKeyLabelValue;
	private TextBox textBoxModel;
	private TextBox textBoxResidue;

	public static int accessKeyLength = 6;
	
	iCingConstants c = iCing.c;
	DecoratorPanel decPanel = new DecoratorPanel();
    final static RichTextArea statusArea = iCing.statusArea;

	int i = 0;
	final int optionVerbosityIdx = i++;
	final int optionImagerIdx = i++;
	final int optionResidueIdx = i++;
	final int optionModelIdx = i++;
	final int optionAccessIdx = i++;
	int cingVerbosity;
    
	public Options() {
		setState(iCing.OPTIONS_STATE);
		
		final VerticalPanel verticalPanelTop = new VerticalPanel();
		initWidget(verticalPanelTop);
		final Label html_1 = new Label( c.Options() );
		html_1.setStylePrimaryName("h1");
		verticalPanelTop.add(html_1);
		verticalPanelTop.add(decPanel);
		
		final VerticalPanel verticalPanel = new VerticalPanel();
		decPanel.setWidget(verticalPanel);

		final FlexTable flexTable = new FlexTable();
		flexTable.setCellSpacing(5);
		flexTable.setCellPadding(5);
		verticalPanel.add(flexTable);

		
		final Label verbosityLabel = new Label(c.Verbosity());
		flexTable.setWidget(optionVerbosityIdx, 0, verbosityLabel);
		
		final ListBox listBoxVerbosity = new ListBox();
		listBoxVerbosity.addItem(c.Nothing(),"0");
		listBoxVerbosity.addItem(c.Error(),"1");
		listBoxVerbosity.addItem(c.Warning(),"2");
		listBoxVerbosity.addItem(c.Output(),"3");
		listBoxVerbosity.addItem(c.Detail(),"4");		
		listBoxVerbosity.addItem(c.Debug(),"9"); // refuse to give up extra space between 4 and 9 for coding convenience here.
		listBoxVerbosity.setVisibleItemCount(1);
		flexTable.setWidget(optionVerbosityIdx, 1, listBoxVerbosity);
		listBoxVerbosity.addChangeListener(new ChangeListener() {
			public void onChange(final Widget sender) {
				int selectedValue = Integer.parseInt( listBoxVerbosity.getValue( listBoxVerbosity.getSelectedIndex()));
				cingVerbosity = General.map2CingVerbosity( selectedValue );
			}
		});
		listBoxVerbosity.setSelectedIndex(General.verbosityOutput);
		cingVerbosity = General.map2CingVerbosity( General.getVerbosity() );
		
		final CheckBox createImageryCheckBox = new CheckBox();
		flexTable.setWidget(optionImagerIdx, 0, createImageryCheckBox);
		createImageryCheckBox.setChecked(false);
		flexTable.getFlexCellFormatter().setColSpan(1, 0, 2);
		createImageryCheckBox.setText(c.Imagery_repor());
		
		final Label residuesLabel = new Label(c.Residues());
		flexTable.setWidget(optionResidueIdx, 0, residuesLabel);

		textBoxResidue = new TextBox();
		flexTable.setWidget(optionResidueIdx, 1, textBoxResidue);
		textBoxResidue.setWidth("100%");
		textBoxResidue.setEnabled(false);

		final Label egResidue175177189Label = new Label(c.E_g_() + " 175,177-189");
		flexTable.setWidget(optionResidueIdx, 2, egResidue175177189Label);

		final Label ensembleModelsLabel = new Label(c.Ensemble_mode() + ":");
		flexTable.setWidget(optionModelIdx, 0, ensembleModelsLabel);

		textBoxModel = new TextBox();
		flexTable.setWidget(optionModelIdx, 1, textBoxModel);
		textBoxModel.setWidth("100%");
		textBoxModel.setEnabled(false);

		final Label egModel219Label = new Label(c.E_g_() + " 2-19");
		flexTable.setWidget(optionModelIdx, 2, egModel219Label);

		final Label accessKeyLabel = new Label(c.Access_key());
		flexTable.setWidget(optionAccessIdx, 0, accessKeyLabel);

		// Added panel for getting better spacing?
		final HorizontalPanel horizontalPanel = new HorizontalPanel();
		flexTable.setWidget(optionAccessIdx, 1, horizontalPanel);
		horizontalPanel.setSpacing(5);

		accessKeyLabelValue = new Label();
		horizontalPanel.add(accessKeyLabelValue);
//		accessKeyLabelValue.setVisibleLength(accessKeyLength+1); // depending on font the last char sometimes doesn't show.

//		final Label az096Label = new Label("[a-Z0-9]{6}");
//		horizontalPanel.add(az096Label);

		final PushButton regeneratePushButton = new PushButton("Up text", "Down text");
		regeneratePushButton.getDownFace().setHTML(c.Randomizing());
		regeneratePushButton.getUpFace().setHTML(c.Regenerate());
		flexTable.setWidget(optionAccessIdx, 2, regeneratePushButton);
		regeneratePushButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				generateAccessKey();
			}
		});
		regeneratePushButton.setHTML(c.Randomizing());
		regeneratePushButton.setText(c.Regenerate());
		regeneratePushButton.setEnabled(false);
//		generateAccessKey(); # TODO: enable to declutter
		
		final Button nextButton = new Button();
		nextButton.setText(c.Next());
		nextButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				icing.onHistoryChanged(iCing.RUN_STATE);					
			}
		});	
		verticalPanelTop.add(nextButton);
		nextButton.setTitle("Submit to CING server.");
		verticalPanelTop.setCellHorizontalAlignment(nextButton, HasHorizontalAlignment.ALIGN_CENTER);
		
	}
	
	public static String getNewAccessKey() {
		String allowedCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
		String result = "";
		for (int i = 1; i <= accessKeyLength; i++) {
			int idxChar = Random.nextInt( allowedCharacters.length() ); // equal chance for A as for others.
			result += allowedCharacters.charAt(idxChar);
			// TODO: generate on server with cross check on availability...
		}
		return result;
	}
	
	protected void generateAccessKey() {		
		String new_access = getNewAccessKey();
		accessKeyLabelValue.setText(new_access);
		iCing.currentAccessKey = new_access;
	}

	public TextBox getTextBoxResidue() {
		return textBoxResidue;
	}

	public TextBox getTextBoxModel() {
		return textBoxModel;
	}
}
