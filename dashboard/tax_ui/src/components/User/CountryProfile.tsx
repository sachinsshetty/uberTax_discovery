// CountryProfile.tsx
import React from 'react';
import { Card, CardContent, List, ListItem, ListItemText, Box, Typography, Divider, Alert } from '@mui/material';
import { CountryProfileData } from './CountryProfileData';

const CountryProfile: React.FC<{ data: CountryProfileData | null }> = ({ data }) => {
  if (!data) {
    return (
      <Card sx={{ backgroundColor: '#112240', border: '1px solid #1e2d4a' }}>
        <CardContent>
          <Alert severity="warning">No country data selected.</Alert>
        </CardContent>
      </Card>
    );
  }

  // Adapt labels for English countries if needed, but for simplicity, keep German structure where applicable
  //const isGerman = data.country.includes('Kroatien');
  // ... rest remains the same, but add conditional labels if desired
  // For now, assume data fields are used directly, user can adjust

  return (
    <Card sx={{ backgroundColor: '#112240', border: '1px solid #1e2d4a' }}>
      <CardContent>
        <Typography variant="h5" fontWeight="600" sx={{ mb: 2, color: 'grey.400' }}>
          Country Profile: {data.country}
        </Typography>
        
        {/* General Data */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 1, color: 'cyan.400' }}>General Data</Typography>
          <List dense>
            <ListItem>
              <ListItemText primary="Mandate Status" secondary={data.mandateStatus} />
            </ListItem>
            <ListItem>
              <ListItemText primary="Archiving Period (Years)" secondary={data.archivingPeriod || 'N/A'} />
            </ListItem>
          </List>
        </Box>

        {/* Scope - Simplified for English */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 1, color: 'cyan.400' }}>Scope</Typography>
          <Box sx={{ ml: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Triggers</Typography>
            <List dense>
              <ListItem><ListItemText primary="Residents" secondary={data.scope.triggers.residents} /></ListItem>
              <ListItem><ListItemText primary="Non-Residents with VAT ID" secondary={data.scope.triggers.nonResidentsWithVatId} /></ListItem>
              <ListItem><ListItemText primary="Logic" secondary={data.scope.triggers.logic} /></ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>B2B</Typography>
            <List dense>
              <ListItem><ListItemText primary="Status" secondary={data.scope.b2b.status} /></ListItem>
              <ListItem><ListItemText primary="Start Date" secondary={data.scope.b2b.startDate} /></ListItem>
              <ListItem><ListItemText primary="Staggered Introduction" secondary={data.scope.b2b.staggered.applies} /></ListItem>
              <ListItem><ListItemText primary="Threshold" secondary={data.scope.b2b.staggered.threshold} /></ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>B2G</Typography>
            <List dense>
              <ListItem><ListItemText primary="Status" secondary={data.scope.b2g.status} /></ListItem>
              <ListItem><ListItemText primary="Start Date" secondary={data.scope.b2g.startDate} /></ListItem>
              <ListItem><ListItemText primary="Staggered Introduction" secondary={data.scope.b2g.staggered.applies} /></ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>B2C</Typography>
            <List dense>
              <ListItem><ListItemText primary="Reporting Obligation" secondary={data.scope.b2c.reportingObligation} /></ListItem>
              <ListItem><ListItemText primary="Start Date" secondary={data.scope.b2c.startDate || 'N/A'} /></ListItem>
            </List>
          </Box>
        </Box>

        {/* Architecture */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 1, color: 'cyan.400' }}>Architecture</Typography>
          <Box sx={{ ml: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Model</Typography>
            <List dense>
              <ListItem><ListItemText primary="Type" secondary={data.architecture.model.type} /></ListItem>
              <ListItem><ListItemText primary="Corner Model" secondary={data.architecture.model.cornerModel} /></ListItem>
              <ListItem><ListItemText primary="Description" secondary={data.architecture.model.description} /></ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Formats</Typography>
            <List dense>
              <ListItem><ListItemText primary="EN16931" secondary={data.architecture.formats.en16931.status} /></ListItem>
              <ListItem><ListItemText primary="National CIUS" secondary={data.architecture.formats.nationalCius.schemaName} /></ListItem>
              <ListItem><ListItemText primary="Allowed Syntaxes" secondary={data.architecture.formats.allowedSyntaxes.join(', ')} /></ListItem>
              <ListItem><ListItemText primary="PDF Conform" secondary={data.architecture.formats.pdfConform} /></ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Transmission</Typography>
            <List dense>
              <ListItem><ListItemText primary="PEPPOL" secondary={data.architecture.transmission.peppol.status} /></ListItem>
            </List>
          </Box>
        </Box>

        {/* Reporting */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 1, color: 'cyan.400' }}>Reporting Obligations</Typography>
          <Box sx={{ ml: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>State Platform</Typography>
            <List dense>
              <ListItem><ListItemText primary="Applies" secondary={data.reporting.statePlatform.applies} /></ListItem>
              <ListItem><ListItemText primary="Name" secondary={data.reporting.statePlatform.name} /></ListItem>
              <ListItem><ListItemText primary="Mandatory" secondary={data.reporting.statePlatform.mandatory} /></ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Clearance</Typography>
            <List dense>
              <ListItem><ListItemText primary="Real-time CTC" secondary={data.reporting.clearance.realTimeCtc} /></ListItem>
              <ListItem><ListItemText primary="Validity After Release" secondary={data.reporting.clearance.validityAfterRelease || 'N/A'} /></ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.300' }}>Reporting Requirements</Typography>
            <List dense>
              <ListItem><ListItemText primary="DRR" secondary={data.reporting.reportingReq.drr} /></ListItem>
              <ListItem><ListItemText primary="Real-time" secondary={data.reporting.reportingReq.realTime} /></ListItem>
              <ListItem><ListItemText primary="Frequency" secondary={data.reporting.reportingReq.frequency || 'N/A'} /></ListItem>
            </List>
          </Box>
        </Box>

        {/* Additional */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 1, color: 'cyan.400' }}>Additional Requirements</Typography>
          <Box sx={{ ml: 2 }}>
            <List dense>
              <ListItem><ListItemText primary="System Certification" secondary={data.additional.systemCert || 'N/A'} /></ListItem>
              <ListItem><ListItemText primary="SAFT Obligation" secondary={data.additional.saft.obligation || 'N/A'} /></ListItem>
              <ListItem><ListItemText primary="Local IDs Obligation" secondary={data.additional.localIds.obligation || 'N/A'} /></ListItem>
              <ListItem><ListItemText primary="Transaction Status Reporting" secondary={data.additional.transactionStatusReporting} /></ListItem>
              <ListItem><ListItemText primary="Special Notes" secondary={data.additional.specialNotes} /></ListItem>
              <ListItem><ListItemText primary="Sanctions" secondary={data.additional.sanctions || 'N/A'} /></ListItem>
            </List>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default CountryProfile;