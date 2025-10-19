import React, { useState, useEffect } from 'react';
import { Container, Grid, Typography, Card, CardContent, List, ListItem, ListItemText, Button, Box, CircularProgress, Alert, Avatar, Divider } from '@mui/material';
import ClientProfiles from './ClientProfiles';

const UserApp = () => {
  const [clients, setClients] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchClients = async (retries = 3) => {
    try {

      const DWANI_API_BASE_URL = import.meta.env.VITE_DWANI_API_BASE_URL || 'localhost';

      // Docker: Use service name; fallback to localhost for local dev
      //const apiUrl = process.env.NODE_ENV === 'development' 
      //  ? 'http://localhost:8000/api/clients' 
      //  : 'http://backend:8000/api/clients';
      const apiUrl = `${DWANI_API_BASE_URL}/api/clients`;


      console.log('Fetching from:', apiUrl);  // Debug log
      
      const res = await fetch(apiUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      const data = await res.json();
      setClients(data);
      console.log('Fetched clients:', data);  // Debug log
    } catch (err) {
      console.error('Error fetching clients:', err);
      if (retries > 0) {
        console.log(`Retrying in 1s... (${retries} left)`);
        setTimeout(() => fetchClients(retries - 1), 1000);
      } else {
        setError('Failed to load clients. Check backend & Docker network.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>Loading clients...</Typography>
      </Container>
    );
  }

  // Compute dynamic stats
  const totalClients = clients.length;
  const impactedClients = clients.filter(c => c.newRegulation !== "N/A" && c.deadline !== null).length;
  const percentageImpacted = totalClients > 0 ? (impactedClients / totalClients) : 0;
  const uniqueNewRegs = [...new Set(clients.filter(c => c.newRegulation !== "N/A" && c.newRegulation !== "UNDER REVIEW" && c.newRegulation !== "MONITORED").map(c => c.newRegulation))].length;
  const percentageNewRegs = totalClients > 0 ? (uniqueNewRegs / totalClients) : 0;

  // Urgency calculation
  const currentDate = new Date('2025-10-12');
  let urgencyLevel = 'LOW';
  let urgencyColor = 'green';
  for (const c of clients) {
    if (c.deadline) {
      const deadline = new Date(c.deadline);
      const daysUntilDeadline = (deadline - currentDate) / (1000 * 60 * 60 * 24);
      if (daysUntilDeadline <= 90) {
        urgencyLevel = 'HIGH';
        urgencyColor = 'red';
        break;
      } else if (daysUntilDeadline <= 180) {
        urgencyLevel = 'MEDIUM';
        urgencyColor = 'orange';
      }
    }
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar sx={{ bgcolor: 'grey.600', mr: 2 }}>
            <Typography variant="h4" fontWeight="bold">AS</Typography>
          </Avatar>
        </Box>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h3" fontWeight="bold" color="grey.200">
            Juris-Diction(AI)ry
          </Typography>
          <Typography variant="body2" color="cyan.400">
            powered by dwani
          </Typography>
        </Box>
        <Box sx={{ width: 64 }} />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          {/* Overview */}
          <Card sx={{ mb: 3, backgroundColor: '#112240', border: '1px solid #1e2d4a' }}>
            <CardContent>
              <Typography variant="h5" fontWeight="600" sx={{ mb: 2, color: 'grey.400' }}>Overview</Typography>
              <Grid container spacing={2} justifyContent="center">
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <CircularProgress variant="determinate" value={percentageImpacted * 100} size={120} thickness={4} sx={{ color: '#3b82f6' }} />
                    <Typography variant="h4" fontWeight="bold" color="blue.400" sx={{ mt: 1 }}>
                      {impactedClients}
                    </Typography>
                    <Typography variant="body2" color="grey.500" sx={{ mt: 1 }}>TOTAL CLIENTS IMPACTED</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <CircularProgress variant="determinate" value={percentageNewRegs * 100} size={120} thickness={4} sx={{ color: '#10b981' }} />
                    <Typography variant="h4" fontWeight="bold" color="green.400" sx={{ mt: 1 }}>
                      {uniqueNewRegs}
                    </Typography>
                    <Typography variant="body2" color="grey.500" sx={{ mt: 1 }}>NEW REGULATIONS</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <CircularProgress variant="determinate" value={urgencyLevel === 'HIGH' ? 20 : urgencyLevel === 'MEDIUM' ? 50 : 0} size={120} thickness={4} sx={{ color: urgencyColor }} />
                    <Typography variant="h5" fontWeight="bold" sx={{ mt: 1, color: urgencyColor === 'red' ? 'red' : urgencyColor === 'orange' ? 'orange' : 'green' }}>
                      {urgencyLevel}
                    </Typography>
                    <Typography variant="body2" color="grey.500" sx={{ mt: 1 }}>URGENCY LEVEL</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Affected Client Profiles */}
          <ClientProfiles clients={clients} />

          {/* Regulatory Feed */}
          <Card sx={{ backgroundColor: '#112240', border: '1px solid #1e2d4a' }}>
            <CardContent>
              <Typography variant="h5" fontWeight="600" sx={{ mb: 2, color: 'grey.400' }}>Regulatory Feed</Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary={<Typography variant="body2" color="cyan.400" fontWeight="600">[Oct 9, 2025] USA:</Typography>}
                    secondary="IRS releases tax inflation adjustments for tax year 2026, including amendments from the One Big Beautiful Bill; standard deduction raised to $15,750 for singles and $31,500 for married filing jointly."
                    secondaryTypographyProps={{ color: 'grey.500', variant: 'body2' }}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary={<Typography variant="body2" color="cyan.400" fontWeight="600">[Oct 9, 2025] USA:</Typography>}
                    secondary="IRS 2025-2026 Priority Guidance Plan outlines key focus areas amid government shutdown impacts."
                    secondaryTypographyProps={{ color: 'grey.500', variant: 'body2' }}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary={<Typography variant="body2" color="cyan.400" fontWeight="600">[Oct 10, 2025] USA:</Typography>}
                    secondary="Treasury and IRS issue proposed regulations for “No Tax on Tips” provision under OBBBA, allowing deduction up to $25,000 for qualified tips."
                    secondaryTypographyProps={{ color: 'grey.500', variant: 'body2' }}
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary={<Typography variant="body2" color="cyan.400" fontWeight="600">[Oct 4, 2025] USA:</Typography>}
                    secondary="One Big Beautiful Bill Act (passed July 2025) introduces $6,000 deduction for individuals age 65+, effective 2025-2028, plus other Trump Tax Plan changes for 2025 filings."
                    secondaryTypographyProps={{ color: 'grey.500', variant: 'body2' }}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ backgroundColor: '#112240', border: '1px solid #1e2d4a', mb: 3 }}>
            <CardContent>
              <Typography variant="h5" fontWeight="600" sx={{ mb: 2, color: 'grey.400' }}>Quick Actions</Typography>
              <Button fullWidth variant="outlined" sx={{ mb: 1, color: '#a8b2d1', borderColor: '#1e2d4a', '&:hover': { bgcolor: '#1e2d4a', color: '#64ffda' } }}>
                Run New Scan
              </Button>
              <Button fullWidth variant="outlined" sx={{ mb: 1, color: '#a8b2d1', borderColor: '#1e2d4a', '&:hover': { bgcolor: '#1e2d4a', color: '#64ffda' } }}>
                Generate Report
              </Button>
              <Button fullWidth variant="outlined" sx={{ mb: 1, color: '#a8b2d1', borderColor: '#1e2d4a', '&:hover': { bgcolor: '#1e2d4a', color: '#64ffda' } }}>
                Client Database
              </Button>
              <Button fullWidth variant="outlined" sx={{ color: '#a8b2d1', borderColor: '#1e2d4a', '&:hover': { bgcolor: '#1e2d4a', color: '#64ffda' } }}>
                Settings
              </Button>
            </CardContent>
          </Card>
          <Card sx={{ backgroundColor: '#112240', border: '1px solid #1e2d4a', mb: 3, textAlign: 'center' }}>
            <CardContent>
              <Typography variant="body2" color="grey.500">
                USER: <Typography component="span" variant="body2" fontWeight="600" color="grey.200">TAX_ADVISOR/USERNAME</Typography>
              </Typography>
              <Typography variant="caption" sx={{ mt: 0.5, display: 'block' }}>LAST UPDATE: JUST NOW</Typography>
            </CardContent>
          </Card>
          <Card sx={{ backgroundColor: '#112240', border: '1px solid #1e2d4a', opacity: 0.2, minHeight: 200 }} />
        </Grid>
      </Grid>
    </Container>
  );
};

export default UserApp;