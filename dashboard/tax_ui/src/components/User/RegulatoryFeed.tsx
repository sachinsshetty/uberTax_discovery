// RegulatoryFeed.tsx - Table component for regulatory feed with search
import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  TextField,
  CircularProgress,
  Box,
  Button,
} from '@mui/material';

interface RegulatoryFeedItem {
  date: string;
  country: string;
  content: string;
}

interface RegulatoryFeedProps {
  feed: RegulatoryFeedItem[];
}

const API_URL = import.meta.env.VITE_DWANI_API_BASE_URL || 'http://localhost:8000';

const RegulatoryFeed: React.FC<RegulatoryFeedProps> = ({ feed }) => {
  const originalData = feed;
  const [filteredData, setFilteredData] = useState<RegulatoryFeedItem[]>([]);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [naturalResponse, setNaturalResponse] = useState('');

  const camelizeKeys = (obj: any): any => {
    const camelize = (str: string): string => str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    
    if (Array.isArray(obj)) {
      return obj.map(camelizeKeys);
    } else if (obj !== null && typeof obj === 'object') {
      return Object.keys(obj).reduce((result, key) => {
        result[camelize(key)] = camelizeKeys(obj[key]);
        return result;
      }, {});
    }
    return obj;
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearchLoading(true);
    setNaturalResponse('');
    setFilteredData([]);
    setSearchResults([]);
    try {
      const url = `${API_URL}/api/clients/natural-query`;
      console.log('Querying natural language search:', url, searchQuery);
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_query: searchQuery, table_name: "regulatory_feed" }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Query HTTP ${response.status}: ${response.statusText} - Body: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Query response:', data);

      setNaturalResponse(data.natural_response || '');

      if (data.results && Array.isArray(data.results)) {
        const camelized = camelizeKeys(data.results);
        // Check if full profile data (has date, country, content)
        if (camelized.length > 0 && camelized[0].date && camelized[0].country && camelized[0].content) {
          setFilteredData(camelized as RegulatoryFeedItem[]);
        } else {
          // Partial data, e.g., only content snippets, show as simple text list
          setSearchResults(camelized);
        }
      } else {
        // Fallback to original data if no results
        setFilteredData(originalData);
      }
    } catch (error) {
      console.error('Error querying regulatory feed:', error);
      // Optionally set an error state
      setFilteredData(originalData);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleClear = () => {
    setFilteredData([]);
    setSearchResults([]);
    setNaturalResponse('');
    setSearchQuery('');
  };

  const displayData = filteredData.length > 0 ? filteredData : originalData;
  const hasSearchResults = searchResults.length > 0;
  const showTable = !hasSearchResults && (displayData.length > 0 || searchLoading);

  return (
    <>
      {/* Search Bar */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, alignItems: 'end', flexWrap: 'wrap' }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask a question about regulatory updates, e.g., Show me updates from EU in 2025"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
          disabled={searchLoading}
          sx={{ 
            '& .MuiOutlinedInput-root': { backgroundColor: '#1e2d4a' },
            flex: 1,
            minWidth: 300,
          }}
        />
        <Button
          variant="contained"
          onClick={handleSearch}
          disabled={searchLoading || !searchQuery.trim()}
          sx={{ minWidth: 100 }}
        >
          {searchLoading ? <CircularProgress size={20} color="inherit" /> : 'Query'}
        </Button>
        {(filteredData.length > 0 || hasSearchResults) && (
          <Button
            variant="outlined"
            onClick={handleClear}
            disabled={searchLoading}
            sx={{ minWidth: 80, color: '#a8b2d1', borderColor: '#1e2d4a' }}
          >
            Clear
          </Button>
        )}
      </Box>

      {/* Natural Response */}
      {naturalResponse && (
        <Box
          sx={{
            mb: 2,
            p: 2,
            backgroundColor: '#1e2d4a',
            border: '1px solid #2a3b5a',
            borderRadius: 1,
          }}
        >
          <Typography sx={{ whiteSpace: 'pre-line', color: 'grey.300', fontSize: '0.875rem' }}>
            {naturalResponse}
          </Typography>
        </Box>
      )}

      {/* Simple Text Box Output for Partial Search Results */}
      {hasSearchResults && (
        <Box
          sx={{
            mb: 2,
            p: 2,
            backgroundColor: '#1e2d4a',
            border: '1px solid #2a3b5a',
            borderRadius: 1,
            maxHeight: 400,
            overflowY: 'auto',
          }}
        >
          <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.400' }}>
            Search Results:
          </Typography>
          {searchResults.map((item, index) => (
            <Typography key={index} variant="body2" sx={{ color: 'grey.300', mb: 0.5 }}>
              {item.content || item.update || 'No content'}
            </Typography>
          ))}
        </Box>
      )}

      {/* Table for Full Feed */}
      {showTable && (
        <Paper sx={{ backgroundColor: '#112240', border: '1px solid #1e2d4a' }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: 'grey.400', fontWeight: '600' }}>Date & Location</TableCell>
                  <TableCell sx={{ color: 'grey.400', fontWeight: '600' }}>Update</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {displayData.map((item, index) => (
                  <TableRow key={index} hover sx={{ '&:hover': { backgroundColor: '#1e2d4a' } }}>
                    <TableCell sx={{ color: 'grey.300' }}>
                      <Typography variant="body2" color="cyan.400" fontWeight="600">
                        [{item.date || 'N/A'}] {item.country || 'Unknown'}:
                      </Typography>
                    </TableCell>
                    <TableCell sx={{ color: 'grey.300' }}>
                      <Typography variant="body2" color="grey.500">
                        {item.content || 'No content'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
                {displayData.length === 0 && searchLoading && (
                  <TableRow>
                    <TableCell colSpan={2} sx={{ textAlign: 'center', py: 4 }}>
                      <CircularProgress size={20} />
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {!showTable && !hasSearchResults && displayData.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4, color: 'grey.500' }}>
          <Typography>No data available.</Typography>
        </Box>
      )}
    </>
  );
};

export default RegulatoryFeed;