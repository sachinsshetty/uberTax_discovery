// CountryProfiles.tsx - Table component for selecting countries
import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Typography } from '@mui/material';
import { CountryProfileData, CountryProfilesData } from './CountryProfileData';  // ES module import

interface CountryProfilesProps {
  onSelectCountry: (country: CountryProfileData) => void;
}

const CountryProfiles: React.FC<CountryProfilesProps> = ({ onSelectCountry }) => {
  return (
    <Paper sx={{ mb: 3, backgroundColor: '#112240', border: '1px solid #1e2d4a' }}>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: 'grey.400', fontWeight: '600' }}>Country</TableCell>
              <TableCell sx={{ color: 'grey.400', fontWeight: '600' }}>Mandate Status</TableCell>
              <TableCell sx={{ color: 'grey.400', fontWeight: '600' }}>B2B Start Date</TableCell>
              <TableCell sx={{ color: 'grey.400', fontWeight: '600' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {CountryProfilesData.map((country, index) => (
              <TableRow key={index} hover sx={{ '&:hover': { backgroundColor: '#1e2d4a' } }}>
                <TableCell sx={{ color: 'grey.300' }}>
                  <Typography variant="body2" fontWeight="500">{country.country}</Typography>
                </TableCell>
                <TableCell sx={{ color: 'grey.300' }}>
                  <Typography variant="body2">{country.mandateStatus}</Typography>
                </TableCell>
                <TableCell sx={{ color: 'grey.300' }}>
                  <Typography variant="body2">{country.scope.b2b.startDate || 'N/A'}</Typography>
                </TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => onSelectCountry(country)}
                    sx={{ color: '#64ffda', borderColor: '#64ffda', '&:hover': { borderColor: '#64ffda', bgcolor: 'rgba(100, 255, 218, 0.04)' } }}
                  >
                    View Details
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default CountryProfiles;