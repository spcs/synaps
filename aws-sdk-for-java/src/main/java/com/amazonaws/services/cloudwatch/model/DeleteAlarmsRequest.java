/*
 * Copyright 2010-2012 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 * 
 *  http://aws.amazon.com/apache2.0
 * 
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
package com.amazonaws.services.cloudwatch.model;
import com.amazonaws.AmazonWebServiceRequest;

/**
 * Container for the parameters to the {@link com.amazonaws.services.cloudwatch.AmazonCloudWatch#deleteAlarms(DeleteAlarmsRequest) DeleteAlarms operation}.
 * <p>
 * Deletes all specified alarms. In the event of an error, no alarms are deleted.
 * </p>
 *
 * @see com.amazonaws.services.cloudwatch.AmazonCloudWatch#deleteAlarms(DeleteAlarmsRequest)
 */
public class DeleteAlarmsRequest extends AmazonWebServiceRequest {

	/**
     * A Project_id of alarms to be deleted.
     * <p>
     * <b>Constraints:</b><br/>
     * <b>Length: </b>1 - 255<br/>
     * <b>Pattern: </b>[^:].*<br/>
     */
    private String project_id;
    
    public String getProject_id() {
		return project_id;
	}

	public void setProject_id(String project_id) {
		this.project_id = project_id;
	}

	/**
     * A list of alarms to be deleted.
     * <p>
     * <b>Constraints:</b><br/>
     * <b>Length: </b>0 - 100<br/>
     */
    private java.util.List<String> alarmNames;

    /**
     * A list of alarms to be deleted.
     * <p>
     * <b>Constraints:</b><br/>
     * <b>Length: </b>0 - 100<br/>
     *
     * @return A list of alarms to be deleted.
     */
    public java.util.List<String> getAlarmNames() {
        
        if (alarmNames == null) {
            alarmNames = new java.util.ArrayList<String>();
        }
        return alarmNames;
    }
    
    /**
     * A list of alarms to be deleted.
     * <p>
     * <b>Constraints:</b><br/>
     * <b>Length: </b>0 - 100<br/>
     *
     * @param alarmNames A list of alarms to be deleted.
     */
    public void setAlarmNames(java.util.Collection<String> alarmNames) {
        if (alarmNames == null) {
            this.alarmNames = null;
            return;
        }

        java.util.List<String> alarmNamesCopy = new java.util.ArrayList<String>(alarmNames.size());
        alarmNamesCopy.addAll(alarmNames);
        this.alarmNames = alarmNamesCopy;
    }
    
    /**
     * A list of alarms to be deleted.
     * <p>
     * Returns a reference to this object so that method calls can be chained together.
     * <p>
     * <b>Constraints:</b><br/>
     * <b>Length: </b>0 - 100<br/>
     *
     * @param alarmNames A list of alarms to be deleted.
     *
     * @return A reference to this updated object so that method calls can be chained 
     *         together. 
     */
    public DeleteAlarmsRequest withAlarmNames(String... alarmNames) {
        if (getAlarmNames() == null) setAlarmNames(new java.util.ArrayList<String>(alarmNames.length));
        for (String value : alarmNames) {
            getAlarmNames().add(value);
        }
        return this;
    }
    
    /**
     * A list of alarms to be deleted.
     * <p>
     * Returns a reference to this object so that method calls can be chained together.
     * <p>
     * <b>Constraints:</b><br/>
     * <b>Length: </b>0 - 100<br/>
     *
     * @param alarmNames A list of alarms to be deleted.
     *
     * @return A reference to this updated object so that method calls can be chained 
     *         together. 
     */
    public DeleteAlarmsRequest withAlarmNames(java.util.Collection<String> alarmNames) {
        if (alarmNames == null) {
            this.alarmNames = null;
        } else {
            java.util.List<String> alarmNamesCopy = new java.util.ArrayList<String>(alarmNames.size());
            alarmNamesCopy.addAll(alarmNames);
            this.alarmNames = alarmNamesCopy;
        }

        return this;
    }
    
    /**
     * Returns a string representation of this object; useful for testing and
     * debugging.
     *
     * @return A string representation of this object.
     *
     * @see java.lang.Object#toString()
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        if (project_id != null) sb.append("Project_id: " + project_id + ", ");
        if (alarmNames != null) sb.append("AlarmNames: " + alarmNames + ", ");
        sb.append("}");
        return sb.toString();
    }
    
    @Override
    public int hashCode() {
        final int prime = 31;
        int hashCode = 1;
        hashCode = prime * hashCode + ((getProject_id() == null) ? 0 : getProject_id().hashCode()); 
        hashCode = prime * hashCode + ((getAlarmNames() == null) ? 0 : getAlarmNames().hashCode()); 
        return hashCode;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null) return false;
    
        if (obj instanceof DeleteAlarmsRequest == false) return false;
        DeleteAlarmsRequest other = (DeleteAlarmsRequest)obj;
        
        if (other.getProject_id() == null ^ this.getProject_id() == null) return false;
        if (other.getProject_id() != null && other.getProject_id().equals(this.getProject_id()) == false) return false; 
        if (other.getAlarmNames() == null ^ this.getAlarmNames() == null) return false;
        if (other.getAlarmNames() != null && other.getAlarmNames().equals(this.getAlarmNames()) == false) return false; 
        return true;
    }
    
}
    