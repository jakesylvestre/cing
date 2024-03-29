package cing.client;

import cing.client.i18n.iCingConstants;

import com.google.gwt.user.client.History;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.VerticalPanel;


public class iCingView extends Composite {

	
	private String state;
	public iCing icing;
	final VerticalPanel verticalPanel = new VerticalPanel();
    final DecoratorPanel decPanel = new DecoratorPanel(); // Almost always used.
    iCingConstants c = iCing.c;
	
	public iCingView() {
		super();
		initWidget(verticalPanel);
		verticalPanel.setSpacing(iCing.margin);		
	}
	
	
	/**
	 * Make the view visible and remember it in browser history
	 * 
	 */
	public void enterView() {
		// Before clearing it; have the browser remember it.
		if (isVisible()) {
			GenClient.showDebug("For view: " + getClass().toString() + " was already visible; no change was made.");
			return;
		}
		String state = getState();
		if (state == null) {
			GenClient.showError("Failed to get state for view" + getClass().toString() + "; making no change");
			return;
		}
//		GenClient.showDebug("Added history item for state: " + state);
		setVisible(true);
		boolean issueEvent = false;
		History.newItem(state, issueEvent);
	}

	/** This routine should not use GenClient.showXXX yet
	 * 
	 * @param icing
	 */
	public void setIcing(iCing icing) {
	    if ( icing ==  null ) {
	        System.err.println("ERROR: CODE BUG in iCingView.setiCing icing is null.");
	        return;
	    }
	    this.icing = icing;
	}

	public void setState(String state) {
		this.state = state;
	}

	public String getState() {
		return state;
	}
}
