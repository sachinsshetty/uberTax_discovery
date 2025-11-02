import React, { useState, useMemo } from 'react';
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

// FIXED: Helper to ensure HTTPS for API URLs (fallback to localhost for dev)
const getApiBaseUrl = (): string => {
  let baseUrl = import.meta.env.VITE_DWANI_API_BASE_URL || 'http://localhost:8000';
  // Force HTTPS in production (detect via window.location)
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    baseUrl = baseUrl.replace(/^http:/, 'https:');
    if (baseUrl.includes('localhost')) {
      baseUrl = 'https://localhost:8000'; // Adjust port if needed; use self-signed cert for local HTTPS
    }
  }
  return baseUrl;
};

const API_URL = getApiBaseUrl();  // FIXED: Use HTTPS-safe URL

interface RegulatoryFeedItem {
  date: string;
  country: string;
  content: string;
}

interface RegulatoryFeedProps {
  feed: RegulatoryFeedItem[];
}

const RegulatoryFeed: React.FC<RegulatoryFeedProps> = ({ feed }) => {
  const originalData = feed;
  const [filteredData, setFilteredData] = useState<RegulatoryFeedItem[]>([]);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [naturalResponse, setNaturalResponse] = useState('');
  const [error, setError] = useState<string | null>(null); // NEW: Error state for UX

  const camelizeKeys = (obj: any): any => {
    const camelize = (str: string): string => str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    
    if (Array.isArray(obj)) {
      return obj.map(camelizeKeys);
    } else if (obj !== null && typeof obj === 'object') {
      // FIXED: Type the accumulator and initial value to include an index signature
      return Object.keys(obj).reduce((result: Record<string, any>, key: string) => {
        result[camelize(key)] = camelizeKeys(obj[key]);
        return result;
      }, {} as Record<string, any>);
    }
    return obj;
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearchLoading(true);
    setNaturalResponse('');
    setFilteredData([]);
    setSearchResults([]);
    setError(null); // NEW: Clear previous errors
    try {
      // FIXED: Use HTTPS-safe API_URL
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
      setError(error instanceof Error ? error.message : 'An unexpected error occurred'); // NEW: Set user-friendly error
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
    setError(null); // NEW: Clear errors on reset
  };

  // NEW: Sort display data by date descending for better UX (most recent first)
  const displayData = useMemo(() => {
    const dataToSort = filteredData.length > 0 ? filteredData : originalData;
    return [...dataToSort].sort((a, b) => {
      const dateA = new Date(a.date).getTime();
      const dateB = new Date(b.date).getTime();
      return dateB - dateA; // Descending
    });
  }, [filteredData, originalData]);

  const hasSearchResults = searchResults.length > 0;
  const showTable = !hasSearchResults && (displayData.length > 0 || searchLoading);
  const shouldScrollTable = displayData.length > 10; // NEW: Conditional scrollbar

  // NEW: Table container styles with conditional maxHeight for scrollbar
  const tableContainerSx = useMemo(() => ({
    maxHeight: shouldScrollTable ? 400 : 'none',
    overflow: shouldScrollTable ? 'auto' : 'visible',
  }), [shouldScrollTable]);

  return (
    <>
      {/* NEW: Component Header for better UX */}
      <Typography variant="h6" sx={{ mb: 2, color: 'grey.300', fontWeight: 600 }}>
        Regulatory Feed Updates
        {displayData.length > 0 && (
          <Typography component="span" variant="body2" sx={{ ml: 1, color: 'grey.500' }}>
            ({displayData.length} items)
          </Typography>
        )}
      </Typography>

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

      {/* NEW: Error Display */}
      {error && (
        <Box
          sx={{
            mb: 2,
            p: 2,
            backgroundColor: '#3d2b1f',
            border: '1px solid #5d4037',
            borderRadius: 1,
            color: 'warning.main',
          }}
        >
          <Typography variant="body2">
            Error: {error}
          </Typography>
        </Box>
      )}

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
            Search Results ({searchResults.length}):
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
          <TableContainer sx={tableContainerSx}>
            {/* NEW: Sticky header for better UX when scrolling */}
            <Table stickyHeader>
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
                      <Typography variant="body2" sx={{ mt: 1, color: 'grey.500' }}>
                        Searching...
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {!showTable && !hasSearchResults && displayData.length === 0 && !searchLoading && (
        <Box sx={{ textAlign: 'center', py: 4, color: 'grey.500' }}>
          <Typography>No data available. Try searching for specific updates!</Typography>
        </Box>
      )}
    </>
  );
};

export default RegulatoryFeed;